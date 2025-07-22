import { useState, useRef } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import { parseSSEStream } from '@/utils';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';
import { v4 as uuidv4 } from 'uuid';

export default function Chatbot() {
  const [sessionIdList, setSessionIdList] = useState([uuidv4()]);
  const [currentSessionId, setCurrentSessionId] = useState(sessionIdList[0]);
  const [messages, setMessages] = useImmer({});
  const fileInputRef = useRef(null);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', currentSessionId);

    try {
      const res = await api.uploadPDF(formData);
      if (!res.ok) {
        const errorData = await res.json();
        console.error('Upload error:', errorData);
        return alert(`Upload failed: ${errorData.message || 'Unknown error'}`);
      }
      console.log('PDF uploaded successfully:', res);
      const data = await res.json();
      console.log('Uploaded:', data);
    } catch (err) {
      console.error('Upload error:', err);
    }
  };

const handleNewChat = async () => {
    const newId = uuidv4();
    setSessionIdList((prev) => [...prev, newId]);
    setCurrentSessionId(newId);

    const question = "Hi";

    // Set user message with correct structure
    setMessages((draft) => {
      draft[newId] = [{ role: 'user', content: question }];
    });

    try {
      console.log('Creating chat...');
      const res = await api.createChat(question, newId);

      if (!res.ok) {
        const errorData = await res.json();
        console.error('Error asking question:', errorData);
        setMessages((draft) => {
          draft[newId].push({
            role: 'assistant',
            content: '',
            error: true
          });
        });
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let aiResponse = '';
      let currentRunId = null;

      for await (const chunk of parseSSEStream(reader, decoder)) {
        // Check if this is a run_id event
        if (chunk.startsWith('[RUN_ID:') && chunk.endsWith(']')) {
          currentRunId = chunk.slice(8, -1); // Extract run_id from [RUN_ID:xxxx]
          console.log('Captured run_id:', currentRunId);
          continue; // Don't add this to the message content
        }
        
        aiResponse += chunk;
        setMessages((draft) => {
          const current = draft[newId] || [];
          const last = current[current.length - 1];
          if (last?.role === 'assistant') {
            last.content = aiResponse;
            last.run_id = currentRunId; // Store run_id in the message
          } else {
            draft[newId].push({ 
              role: 'assistant', 
              content: aiResponse,
              run_id: currentRunId 
            });
          }
        });
      }
    } catch (err) {
      console.error('Chat creation error:', err);
      setMessages((draft) => {
        draft[newId].push({
          role: 'assistant',
          content: '',
          error: true
        });
      });
    }
  };

  const handleAsk = async (question) => {
  const sessionId = currentSessionId;

  setMessages((draft) => {
    draft[sessionId] = [
      ...(draft[sessionId] || []),
      { role: 'user', content: question },
    ];
  });

  const res = await api.askQuestion(sessionId, question);
  if (!res.ok) {
    const errorData = await res.json();
    console.error('Error asking question:', errorData);
    setMessages((draft) => {
      draft[sessionId].push({
        role: 'assistant',
        content: '',
        error: true,
      });
    });
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let aiResponse = '';
  let currentRunId = null;

  for await (const chunk of parseSSEStream(reader, decoder)) {
    // Check if this is a run_id event
    if (chunk.startsWith('[RUN_ID:') && chunk.endsWith(']')) {
      currentRunId = chunk.slice(8, -1); // Extract run_id from [RUN_ID:xxxx]
      console.log('Captured run_id:', currentRunId);
      continue; // Don't add this to the message content
    }
    
    aiResponse += chunk;
    setMessages((draft) => {
      const current = draft[sessionId] || [];
      const last = current[current.length - 1];
      if (last?.role === 'assistant') {
        last.content = aiResponse;
        last.run_id = currentRunId; // Store run_id in the message
      } else {
        draft[sessionId].push({ 
          role: 'assistant', 
          content: aiResponse,
          run_id: currentRunId 
        });
      }
    });
  }
};


  const handleFileButtonClick = () => fileInputRef.current.click();

  return (
    <div className="flex h-full w-full bg-gray-900 text-white">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">Chats</h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {sessionIdList.map((id, idx) => (
            <button
              key={id}
              className={`block w-full text-left px-3 py-2 rounded transition-colors ${
                currentSessionId === id
                  ? 'bg-gray-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
              onClick={() => setCurrentSessionId(id)}
            >
              Chat {idx + 1}
            </button>
          ))}
        </div>
        <div className="p-4 border-t border-gray-700">
          <button
            className="w-full bg-gray-600 text-white py-2 rounded hover:bg-gray-500 transition-colors"
            onClick={handleNewChat}
          >
            + New Chat
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto p-4">
            <ChatMessages 
              messages={messages[currentSessionId] || []} 
              sessionId={currentSessionId} 
            />
          </div>
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-700 bg-gray-800 p-4">
          <div className="max-w-4xl mx-auto flex items-end gap-3">
            <div className="flex-1">
              <ChatInput onSubmit={handleAsk} />
            </div>
            <button
              onClick={handleFileButtonClick}
              className="p-2 rounded bg-gray-600 hover:bg-gray-500 text-white transition-colors"
              title="Upload PDF"
            >
              📄
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf"
              className="hidden"
              onChange={(e) => {
                if (e.target.files[0]) handleUpload(e.target.files[0]);
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
