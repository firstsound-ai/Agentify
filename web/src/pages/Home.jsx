import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Button, Typography, Toast, TextArea, Space } from '@douyinfe/semi-ui';
import { IconFlipHorizontal } from '@douyinfe/semi-icons';
import './Home.css'; 
import request from '../utils/request';

const { Content } = Layout;
const { Title, Text } = Typography;

const AnimatedTitle = ({ text, style }) => {
  const [visibleChars, setVisibleChars] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setVisibleChars(prev => {
        if (prev < text.length) {
          return prev + 1;
        }
        clearInterval(timer);
        return prev;
      });
    }, 150);
    
    return () => clearInterval(timer);
  }, [text]);
  
  return (
    <Title style={style}>
      {text.split('').map((char, index) => (
        <span
          key={index}
          className={`animated-char ${index < visibleChars ? 'visible' : ''}`}
          style={{
            animationDelay: `${index * 0.15}s`
          }}
        >
          {char}
        </span>
      ))}
    </Title>
  );
};

function Home() {
  const navigate = useNavigate();
  const [mainInput, setMainInput] = useState(''); 
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('正在创建需求...');

  // 创建需求并获取thread_id的函数
  const createRequirement = async (userInput) => {
    try {
      const result = await request.post('/api/requirement/create', {
        initial_requirement: userInput
      });
      
      if (result.code === 0) {
        return result.data.thread_id;
      } else {
        throw new Error(result.message || '创建需求失败');
      }
    } catch (error) {
      console.error('创建需求失败:', error);
      Toast.error('创建需求失败，请重试');
      throw error;
    }
  };

  // 获取需求状态的函数
  const getRequirementStatus = async (threadId) => {
    try {
      const result = await request.get(`/api/requirement/status/${threadId}`);
      return result;
    } catch (error) {
      console.error('获取需求状态失败:', error);
      Toast.error('获取状态失败，请重试');
      throw error;
    }
  };

  // 轮询获取状态直到问卷生成完成
  const pollRequirementStatus = async (threadId, userInput) => {
    const maxAttempts = 30; // 最多轮询30次
    const interval = 2000; // 每2秒轮询一次
    let attempts = 0;

    const poll = async () => {
      try {
        attempts++;
        setLoadingText(`正在生成问卷... (${attempts}/${maxAttempts})`);
        
        const statusResult = await getRequirementStatus(threadId);
        console.log('轮询状态结果:', statusResult);

        if (statusResult.data.status === 'waiting_for_answers' && statusResult.data.questionnaire) {
          // 问卷已生成，跳转到问卷页面
          navigate('/questionnaire', { 
            state: { 
              userInput: userInput,
              threadId: threadId,
              questionnaire: statusResult.data.questionnaire
            } 
          });
          return;
        } else if (statusResult.data.status === 'pending') {
          // 还在处理中，继续轮询
          if (attempts < maxAttempts) {
            setTimeout(poll, interval);
          } else {
            throw new Error('生成问卷超时，请重试');
          }
        } else if (statusResult.data.error) {
          // 有错误
          throw new Error(statusResult.data.error);
        } else {
          // 其他状态，继续轮询
          if (attempts < maxAttempts) {
            setTimeout(poll, interval);
          } else {
            throw new Error('生成问卷超时，请重试');
          }
        }
      } catch (error) {
        console.error('轮询失败:', error);
        Toast.error(error.message || '处理失败，请重试');
        setIsLoading(false);
      }
    };

    // 开始轮询
    poll();
  };

  const handleMainSubmit = async () => {
    if (!mainInput.trim()) return;

    setIsLoading(true);
    setLoadingText('正在创建需求...');
    
    try {
      // 第一步：创建需求并获取thread_id
      const threadId = await createRequirement(mainInput.trim());
      console.log('获取到thread_id:', threadId);

      // 第二步：开始轮询状态
      await pollRequirementStatus(threadId, mainInput.trim());

    } catch (error) {
      console.error('处理失败:', error);
      setIsLoading(false);
    }
  };

  const handleMainInputKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleMainSubmit();
    }
  };

  // 快捷提示词
  const quickPrompts = [
    "帮我写一份工作报告",
    "分析这个项目的可行性",
    "制定学习计划",
    "写一个产品介绍"
  ];

  return (
    <Content className="chat-content">
      <div className="chat-container">
        {/* 主要输入区域 */}
        <div className="main-input-section">
          <div className="welcome-header">
            <AnimatedTitle 
              text="让你的想法变为现实！"
              style={{ 
                fontSize: '56px', 
                margin: 16, 
                textAlign: 'center', 
                color: '#000000'
              }}
            />
            <Text type="secondary" style={{ fontSize: '16px', textAlign: 'center', marginTop: '24px' }}>
              描述您想要完成的任务，我会为您自动构建APP
            </Text>
          </div>

          <div className="simple-input-section">
            <TextArea
              placeholder="例如：我需要写一份关于AI技术发展的报告，包含市场分析、技术趋势和未来展望..."
              value={mainInput}
              onChange={setMainInput}
              onKeyPress={handleMainInputKeyPress}
              autosize={{ minRows: 4, maxRows: 12 }}
              className="main-textarea"
              maxCount={2000}
              showClear
              disabled={isLoading}
            />
            <div className="button-section">
              <Button
                theme="solid" 
                type="primary" 
                icon={<IconFlipHorizontal />}
                onClick={handleMainSubmit} 
                disabled={!mainInput.trim() || isLoading}
                size="large"
                className="submit-button"
                loading={isLoading}
              >
                {isLoading ? loadingText : '开始创作'}
              </Button>
            </div>
          </div>

          <div className="quick-prompts" style={{ marginTop: '24px' }}>
            <Text type="secondary" style={{ marginBottom: '12px', display: 'block' }}>
              或者试试这些：
            </Text>
            <Space wrap>
              {quickPrompts.map((prompt, index) => (
                <Button
                  key={index}
                  type="tertiary"
                  theme="borderless"
                  onClick={() => setMainInput(prompt)}
                  disabled={isLoading}
                  style={{
                    borderRadius: '20px',
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #e9ecef',
                    padding: '8px 16px'
                  }}
                >
                  {prompt}
                </Button>
              ))}
            </Space>
          </div>
        </div>
      </div>
    </Content>
  );
}

export default Home;