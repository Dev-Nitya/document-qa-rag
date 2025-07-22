import Markdown from 'react-markdown';
import useAutoScroll from '@/hooks/useAutoScroll';
import Spinner from '@/components/Spinner';
import userIcon from '@/assets/images/user.svg';
import errorIcon from '@/assets/images/error.svg';
import api from '@/api';

function ChatMessages({ messages, isLoading, sessionId }) {
  const scrollContentRef = useAutoScroll(isLoading);

  const handleFeedback = async (messageIndex, isPositive) => {
    const currentMessage = messages[messageIndex];
    const previousMessage = messages[messageIndex - 1];

    if (!currentMessage || currentMessage.role !== 'assistant' || !previousMessage) {
      console.error('Invalid message for feedback');
      return;
    }

    try {
      await api.submitFeedback({
        session_id: sessionId,
        question: previousMessage.content,
        answer: currentMessage.content,
        feedback: isPositive ? 'thumbs_up' : 'thumbs_down',
        comment: '',
        run_id: currentMessage.run_id || null // Include run_id in feedback
      });
      
      alert(`Feedback ${isPositive ? '👍' : '👎'} submitted successfully!`);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Failed to submit feedback. Please try again.');
    }
  };
  
  return (
    <div ref={scrollContentRef} className='grow space-y-4'>
      {messages.map(({ role, content, loading, error }, idx) => (
        <div key={idx} className={`flex items-start gap-4 py-4 px-3 rounded-xl ${role === 'user' ? 'bg-gray-700/50' : 'bg-gray-800/30'}`}>
          {role === 'user' && (
            <img
              className='h-[26px] w-[26px] shrink-0 filter invert'
              src={userIcon}
              alt='user'
            />
          )}
          <div className="text-white flex-1">
            <div className='markdown-container prose prose-invert max-w-none'>
              {(loading && !content) ? <Spinner />
                : (role === 'assistant')
                  ? <Markdown>{content}</Markdown>
                  : <div className='whitespace-pre-line text-white'>{content}</div>
              }
            </div>
            {error && (
              <div className={`flex items-center gap-1 text-sm text-red-400 ${content && 'mt-2'}`}>
                <img className='h-5 w-5 filter brightness-0 invert hue-rotate-0 saturate-100' src={errorIcon} alt='error' />
                <span>Error generating the response</span>
              </div>
            )}
            
            {/* Feedback buttons for AI messages */}
            {role === 'assistant' && content && !loading && !error && (
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => handleFeedback(idx, true)}
                  className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                  title="Good response"
                >
                  👍
                </button>
                <button
                  onClick={() => handleFeedback(idx, false)}
                  className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                  title="Bad response"
                >
                  👎
                </button>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ChatMessages;