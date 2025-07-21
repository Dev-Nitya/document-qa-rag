import Markdown from 'react-markdown';
import useAutoScroll from '@/hooks/useAutoScroll';
import Spinner from '@/components/Spinner';
import userIcon from '@/assets/images/user.svg';
import errorIcon from '@/assets/images/error.svg';

function ChatMessages({ messages, isLoading }) {
  const scrollContentRef = useAutoScroll(isLoading);
  
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
          <div className="text-white">
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
          </div>
        </div>
      ))}
    </div>
  );
}

export default ChatMessages;