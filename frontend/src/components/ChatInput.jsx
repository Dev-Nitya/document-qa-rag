import { useState } from 'react';
import useAutosize from '@/hooks/useAutosize';
import sendIcon from '@/assets/images/send.svg';

function ChatInput({ onSubmit }) {
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const textareaRef = useAutosize(newMessage);

  const submitNewMessage = async () => {
    if (!newMessage.trim() || isLoading) return;
    
    const message = newMessage.trim();
    setNewMessage('');
    setIsLoading(true);
    
    try {
      await onSubmit(message);
    } finally {
      setIsLoading(false);
    }
  };

  function handleKeyDown(e) {
    if(e.keyCode === 13 && !e.shiftKey && !isLoading) {
      e.preventDefault();
      submitNewMessage();
    }
  }
  
  return(
    <div className='w-full'>
      <div className='p-1.5 bg-gray-600/35 rounded-xl'>
        <div className='pr-0.5 bg-gray-800 relative shrink-0 rounded-xl overflow-hidden ring-gray-600 ring-1 focus-within:ring-2 transition-all'>
          <textarea
            className='block w-full max-h-[140px] py-3 px-4 pr-11 bg-gray-800 text-white rounded-xl resize-none placeholder:text-gray-400 focus:outline-none'
            ref={textareaRef}
            rows='1'
            value={newMessage}
            onChange={e => setNewMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder={isLoading ? "Sending..." : "Type your message..."}
          />
          <button
            className={`absolute top-1/2 -translate-y-1/2 right-3 p-1 rounded-md hover:bg-gray-600/20 text-white transition-colors ${
              isLoading || !newMessage.trim() ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={submitNewMessage}
            disabled={isLoading || !newMessage.trim()}
          >
            <img src={sendIcon} alt='send' className="filter invert w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatInput;