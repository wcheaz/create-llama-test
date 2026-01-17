// This file contains a client-side fix for the JSON parsing error in streaming responses
// It should be included in the UI to handle malformed JSON chunks

// Store for incomplete chunks that might be part of a larger JSON object
let incompleteChunk = '';

// Enhanced JSON parser that handles incomplete chunks
function safeJSONParse(chunk) {
    try {
        // First try to parse the chunk directly
        return JSON.parse(chunk);
    } catch (error) {
        // If that fails, try to combine with any incomplete chunk from before
        if (incompleteChunk) {
            try {
                const combined = incompleteChunk + chunk;
                const result = JSON.parse(combined);
                incompleteChunk = ''; // Clear the buffer if successful
                return result;
            } catch (e) {
                // Still failed, update the incomplete chunk
                incompleteChunk += chunk;
                return null;
            }
        } else {
            // Store the chunk as incomplete and try to fix common issues
            incompleteChunk = chunk;
            
            // Try to fix common JSON issues
            let fixed = chunk;
            
            // Fix unterminated strings by adding closing quote if needed
            const quoteCount = (fixed.match(/"/g) || []).length;
            if (quoteCount % 2 !== 0) {
                fixed += '"';
            }
            
            // Fix unterminated objects
            const openBraces = (fixed.match(/{/g) || []).length;
            const closeBraces = (fixed.match(/}/g) || []).length;
            if (openBraces > closeBraces) {
                fixed += '}'.repeat(openBraces - closeBraces);
            }
            
            // Try parsing the fixed version
            try {
                const result = JSON.parse(fixed);
                incompleteChunk = ''; // Clear if successful
                return result;
            } catch (e) {
                // Still failed, return null to indicate we couldn't parse
                return null;
            }
        }
    }
}

// Monkey patch the fetch API or EventSource to use our safe parser
if (typeof window !== 'undefined') {
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        return originalFetch.apply(this, args).then(response => {
            // Check if this is a streaming response
            if (response.body && response.headers.get('content-type')?.includes('application/json')) {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                let chunks = [];
                
                return new Response(new ReadableStream({
                    start(controller) {
                        function pump() {
                            return reader.read().then(({ done, value }) => {
                                if (done) {
                                    controller.close();
                                    return;
                                }
                                
                                const chunk = decoder.decode(value, { stream: true });
                                const lines = chunk.split('\n');
                                
                                for (const line of lines) {
                                    if (line.trim()) {
                                        try {
                                            const parsed = safeJSONParse(line);
                                            if (parsed) {
                                                chunks.push(parsed);
                                            }
                                        } catch (e) {
                                            console.warn('Failed to parse chunk:', line, e);
                                        }
                                    }
                                }
                                
                                controller.enqueue(value);
                                return pump();
                            });
                        }
                        
                        return pump();
                    }
                }), {
                    status: response.status,
                    statusText: response.statusText,
                    headers: response.headers
                });
            }
            
            return response;
        });
    };
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { safeJSONParse };
}