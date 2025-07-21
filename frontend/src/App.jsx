import Chatbot from '@/components/Chatbot';
import logo from '@/assets/images/logo.svg';

function App() {

  return (
    <div className='h-screen w-full bg-gray-900 flex flex-col overflow-hidden'>
      <header className='shrink-0 bg-gray-800 border-b border-gray-700 px-4 py-3'>
        <div className='flex items-center gap-3'>
          <a href='https://codeawake.com'>
            <img src={logo} className='w-8 h-8 filter invert' alt='logo' />
          </a>
          <h1 className='font-urbanist text-lg font-semibold text-white'>Tech Trends AI Chatbot</h1>
        </div>
      </header>
      <div className='flex-1 overflow-hidden'>
        <Chatbot />
      </div>
    </div>
  );
}

export default App;