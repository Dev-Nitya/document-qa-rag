const BASE_URL = import.meta.env.VITE_API_URL;

async function uploadPDF(formData) {
  const res = await fetch(BASE_URL + '/upload', {
    method: 'POST',
    body: formData, // Do NOT manually set headers here
  });

  if (!res.ok) {
    return Promise.reject({ status: res.status, data });
  }

  return res;
}

async function sendFeedback(index, isPositive) {
  const msg = messages[index];
  const prevMsg = messages[index - 1];

  if (!msg || msg.role !== 'assistant' || msg.loading || msg.error || !prevMsg) return;

  try {
    await api.submitFeedback({
      question: prevMsg.content,
      session_id: chatId || 'anonymous',
      answer: msg.content,
      feedback: isPositive ? 'thumbs_up' : 'thumbs_down',
    });
    alert(`Feedback ${isPositive ? '👍' : '👎'} submitted`);
  } catch (err) {
    console.error('Feedback error:', err);
    alert('Failed to send feedback');
  }
}


async function createChat(question, session_id) {
  const res = await fetch(BASE_URL + '/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id })
  });
  if (!res.ok) {
    return Promise.reject({ status: res.status, data });
  }
  return res;
}

async function askQuestion(sessionId, question) {
  const res = await fetch(BASE_URL + `/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question })
  });
  if (!res.ok) {
    return Promise.reject({ status: res.status, data: await res.json() });
  }
  return res;
}

export default {
  createChat, askQuestion, uploadPDF, sendFeedback
};