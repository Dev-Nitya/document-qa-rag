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

async function submitFeedback(feedbackData) {
  const res = await fetch(BASE_URL + '/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedbackData)
  });

  console.log('Submitting feedback:', feedbackData);
  console.log('Response status:', res.status);
  
  if (!res.ok) {
    const errorData = await res.json();
    return Promise.reject({ status: res.status, data: errorData });
  }
  
  return res;
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
  createChat, askQuestion, uploadPDF, submitFeedback
};