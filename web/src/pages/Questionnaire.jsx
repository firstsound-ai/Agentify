import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Button, Typography, Card, Radio, Progress, Space, Spin, Input, TextArea, Toast } from '@douyinfe/semi-ui';
import { IconArrowLeft, IconArrowRight } from '@douyinfe/semi-icons';
import request from '../utils/request';
import './Questionnaire.css';

const { Content } = Layout;
const { Title, Text } = Typography;

function Questionnaire() {
  const navigate = useNavigate();
  const location = useLocation();
  const userInput = location.state?.userInput || '';
  const threadId = location.state?.threadId || '';
  const questionnaire = location.state?.questionnaire || null;
  
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [customAnswers, setCustomAnswers] = useState({}); 
  const [isComplete, setIsComplete] = useState(false);
  const [isShowingAdditionalRequirements, setIsShowingAdditionalRequirements] = useState(false);
  const [additionalRequirements, setAdditionalRequirements] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!questionnaire || !questionnaire.questions) {
    return (
      <Content className="questionnaire-content">
        <div className="questionnaire-container">
          <Card className="question-card">
            <div className="completion-card">
              <Title heading={2} style={{ textAlign: 'center', color: '#1a202c' }}>
                问卷数据加载失败
              </Title>
              <Text style={{ textAlign: 'center', fontSize: '16px', color: '#666', marginBottom: '24px' }}>
                无法获取问卷数据，请返回重试
              </Text>
              <div style={{ textAlign: 'center' }}>
                <Button onClick={() => navigate('/')} type="primary">
                  返回首页
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </Content>
    );
  }

  const questions = questionnaire.questions;

  const isCurrentAnswered = () => {
    const question = questions[currentQuestion];
    const answer = answers[question.id];

    if (question.allow_custom && answer === 'CUSTOM') {
      return customAnswers[question.id] && customAnswers[question.id].trim();
    }
    
    return !!answer;
  };

  const handleAnswer = (questionId, value) => {
    setAnswers({
      ...answers,
      [questionId]: value
    });

    if (value !== 'CUSTOM') {
      const newCustomAnswers = { ...customAnswers };
      delete newCustomAnswers[questionId];
      setCustomAnswers(newCustomAnswers);
    }
  };

  const handleCustomAnswer = (questionId, value) => {
    setCustomAnswers({
      ...customAnswers,
      [questionId]: value
    });
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // 显示额外需求输入界面
      setIsShowingAdditionalRequirements(true);
    }
  };

  const submitAnswers = async () => {
    setIsSubmitting(true);
    
    try {
      const answersArray = [];
      
      questions.forEach(question => {
        const answer = answers[question.id];
        if (answer === 'CUSTOM' && customAnswers[question.id]) {
          // 自定义答案
          answersArray.push({
            question_id: question.id,
            custom_input: customAnswers[question.id].trim()
          });
        } else if (answer) {
          // 选项答案
          answersArray.push({
            question_id: question.id,
            selected_option: answer
          });
        }
      });

      const submissionData = {
        answers: answersArray,
        additional_requirements: additionalRequirements.trim() || null
      };

      console.log('提交的答案数据:', submissionData);

      // 调用API提交答案
      const result = await request.post(`/api/requirement/submit-answers/${threadId}`, submissionData);
      
      if (result.code === 0) {
        // Toast.success('答案提交成功！');
        setIsComplete(true);
        
        // 3秒后跳转到生成页面
        setTimeout(() => {
          navigate('/generate', { 
            state: { 
              userInput,
              threadId,
              answers: submissionData
            } 
          });
        }, 3000);
      } else {
        throw new Error(result.message || '提交失败');
      }
    } catch (error) {
      console.error('提交答案失败:', error);
      Toast.error('提交失败，请重试');
      setIsSubmitting(false);
    }
  };

  const handlePrevious = () => {
    if (isShowingAdditionalRequirements) {
      setIsShowingAdditionalRequirements(false);
    } else if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSkipAdditionalRequirements = () => {
    setAdditionalRequirements('');
    submitAnswers();
  };

  const handleSubmitWithAdditionalRequirements = () => {
    submitAnswers();
  };

  const progress = isShowingAdditionalRequirements 
    ? 100 
    : ((currentQuestion + 1) / questions.length) * 100;

  // 生成中状态
  if (isComplete) {
    return (
      <Content className="questionnaire-content">
        <div className="questionnaire-container">
          <Card className="question-card">
            <div className="completion-card">
              <div className="generating-icon">
                <Spin size="large" />
              </div>
              <Title heading={2} style={{ textAlign: 'center', margin: '24px 0', color: '#1a202c' }}>
                正在生成应用...
              </Title>
              <Text style={{ textAlign: 'center', fontSize: '16px', color: '#666' }}>
                我们正在根据您的需求和答案创建定制化的应用方案，请稍候片刻
              </Text>
            </div>
          </Card>
        </div>
      </Content>
    );
  }

  // 额外需求输入界面
  if (isShowingAdditionalRequirements) {
    return (
      <Content className="questionnaire-content">
        <div className="questionnaire-container">
          <div className="questionnaire-header">
            <Button 
              icon={<IconArrowLeft />} 
              theme="borderless"
              onClick={() => navigate('/')}
              style={{ marginBottom: '8px', color: '#000000' }}
            >
              返回首页
            </Button>

            <div className="user-input-summary">
              <Text type="secondary" size="large">为了更好地创建您的应用，我们跟您明确几个问题！</Text>
              <Text style={{ 
                display: 'block', 
                marginTop: '4px',
                padding: '8px 12px',
                background: '#f8fafc',
                borderRadius: '8px',
                fontSize: '14px'
              }}>
                {userInput}
              </Text>
            </div>
          </div>

          <Card className="question-card">
            <div className="progress-section">
              <div className="progress-info">
                <Text style={{ fontSize: '14px', color: '#666' }}>
                  额外需求 (可选)
                </Text>
                <Text style={{ fontSize: '14px', color: '#666' }}>
                  100% 完成
                </Text>
              </div>
              <Progress 
                percent={100} 
                showInfo={false}
                stroke="#374151"
                style={{ marginTop: '8px' }}
              />
            </div>

            <div className="question-content">
              <Title heading={3} style={{ marginBottom: '24px', color: '#1a202c' }}>
                是否有其他额外需求？
              </Title>

              <div className="additional-requirements-container">
                <Text type="secondary" style={{ marginBottom: '16px', display: 'block' }}>
                  您可以在这里补充任何额外的需求或说明，这将帮助我们更好地为您定制应用。此步骤为可选项，您也可以直接跳过。
                </Text>
                
                <TextArea
                  placeholder="例如：希望界面风格简洁现代，支持多语言切换，需要数据导出功能等..."
                  value={additionalRequirements}
                  onChange={setAdditionalRequirements}
                  autosize={{ minRows: 4, maxRows: 8 }}
                  maxLength={500}
                  showClear
                  disabled={isSubmitting}
                  style={{
                    borderRadius: '12px',
                    border: '1px solid #e2e8f0'
                  }}
                />
                
                <Text type="tertiary" size="small" style={{ marginTop: '8px', display: 'block' }}>
                  {additionalRequirements.length}/500 字符
                </Text>
              </div>
            </div>

            <div className="question-navigation">
              <Button 
                icon={<IconArrowLeft />}
                onClick={handlePrevious}
                disabled={isSubmitting}
                style={{ color: '#000000' }}
              >
                上一题
              </Button>

              <Space>
                <Button 
                  onClick={handleSkipAdditionalRequirements}
                  disabled={isSubmitting}
                  style={{ color: '#000000' }}
                >
                  跳过
                </Button>
                
                <Button 
                  type="primary"
                  onClick={handleSubmitWithAdditionalRequirements}
                  loading={isSubmitting}
                  style={{ color: '#000000' }}
                >
                  {isSubmitting ? '提交中...' : '完成提交'}
                </Button>
              </Space>
            </div>
          </Card>
        </div>
      </Content>
    );
  }

  // 常规问题界面
  const question = questions[currentQuestion];

  return (
    <Content className="questionnaire-content">
      <div className="questionnaire-container">
        <div className="questionnaire-header">
          <Button 
            icon={<IconArrowLeft />} 
            theme="borderless"
            onClick={() => navigate('/')}
            style={{ marginBottom: '8px', color: '#000000' }}
          >
            返回首页
          </Button>

          <div className="user-input-summary">
            <Text type="secondary" size="large">为了更好地创建您的应用，我们跟您明确几个问题！</Text>
            <Text style={{ 
              display: 'block', 
              marginTop: '4px',
              padding: '8px 12px',
              background: '#f8fafc',
              borderRadius: '8px',
              fontSize: '14px'
            }}>
              {userInput}
            </Text>
          </div>
        </div>

        <Card className="question-card">
          <div className="progress-section">
            <div className="progress-info">
              <Text style={{ fontSize: '14px', color: '#666' }}>
                问题 {currentQuestion + 1} / {questions.length}
              </Text>
              <Text style={{ fontSize: '14px', color: '#666' }}>
                {Math.round(progress)}% 完成
              </Text>
            </div>
            <Progress 
              percent={progress} 
              showInfo={false}
              stroke="#374151"
              style={{ marginTop: '8px' }}
            />
          </div>

          <div className="question-content">
            <Title heading={3} style={{ marginBottom: '24px', color: '#1a202c' }}>
              {question.question}
            </Title>

            <div className="options-container">
              <Radio.Group 
                value={answers[question.id]} 
                onChange={(e) => handleAnswer(question.id, e.target.value)}
                direction="vertical"
              >
                {question.options.map((option) => (
                  <div key={option.value} className="option-item">
                    <Radio value={option.value}>
                      <div className="option-content">
                        <div className="option-label">{option.label}</div>
                      </div>
                    </Radio>
                  </div>
                ))}
                
                {/* 如果允许自定义，添加自定义选项 */}
                {question.allow_custom && (
                  <div className="option-item custom-option">
                    <Radio value="CUSTOM">
                      <div className="option-content">
                        <div className="option-label">其他（请说明）</div>
                      </div>
                    </Radio>
                    {answers[question.id] === 'CUSTOM' && (
                      <div className="custom-input-container">
                        <Input
                          placeholder="请输入您的具体需求..."
                          value={customAnswers[question.id] || ''}
                          onChange={(value) => handleCustomAnswer(question.id, value)}
                          maxLength={200}
                          showClear
                          style={{ marginTop: '12px', marginLeft: '32px' }}
                        />
                      </div>
                    )}
                  </div>
                )}
              </Radio.Group>
            </div>
          </div>

          <div className="question-navigation">
            <Button 
              icon={<IconArrowLeft />}
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
              style={{ visibility: currentQuestion === 0 ? 'hidden' : 'visible', color: '#000000' }}
            >
              上一题
            </Button>

            <Button 
              type="primary"
              icon={<IconArrowRight />}
              iconPosition="right"
              onClick={handleNext}
              disabled={!isCurrentAnswered()}
              style={{ color: '#000000' }}
            >
              {currentQuestion === questions.length - 1 ? '下一步' : '下一题'}
            </Button>
          </div>
        </Card>
      </div>
    </Content>
  );
}

export default Questionnaire;