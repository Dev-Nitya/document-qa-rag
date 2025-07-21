export async function* parseSSEStream(reader, decoder) {
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    let lines = buffer.split('\n');
    buffer = lines.pop(); // Keep the last incomplete line in the buffer

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim();
        if (data && data !== '[DONE]') {
          yield data;
        }
      }
    }
  }

  // Handle any remaining data in the buffer
  if (buffer.startsWith('data: ')) {
    const data = buffer.slice(6).trim();
    if (data && data !== '[DONE]') {
      yield data;
    }
  }
}