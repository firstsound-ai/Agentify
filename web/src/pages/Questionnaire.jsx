import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Layout,
  Button,
  Typography,
  Card,
  Radio,
  Progress,
  Space,
  Spin,
  Input,
  TextArea
} from "@douyinfe/semi-ui";
import { IconArrowLeft, IconArrowRight } from "@douyinfe/semi-icons";
import request from "../utils/request";
import "./Questionnaire.css";

const { Content } = Layout;
const { Title, Text } = Typography;

function Questionnaire() {
  const navigate = useNavigate();
  const location = useLocation();
  const userInput = location.state?.userInput || "";
  const threadId = location.state?.threadId || "";
  const questionnaire = location.state?.questionnaire || null;

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [customAnswers, setCustomAnswers] = useState({});
  const [isComplete, setIsComplete] = useState(false);
  const [isShowingAdditionalRequirements, setIsShowingAdditionalRequirements] =
    useState(false);
  const [additionalRequirements, setAdditionalRequirements] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingText, setLoadingText] = useState("正在生成应用...");
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [currentLoadingStep, setCurrentLoadingStep] = useState("");

  if (!questionnaire || !questionnaire.questions) {
    return (
      <Content className="questionnaire-content">
        <div className="questionnaire-container">
          <Card className="question-card">
            <div className="completion-card">
              <Title
                heading={2}
                style={{ textAlign: "center", color: "#1a202c" }}
              >
                问卷数据加载失败
              </Title>
              <Text
                style={{
                  textAlign: "center",
                  fontSize: "16px",
                  color: "#666",
                  marginBottom: "24px",
                }}
              >
                无法获取问卷数据，请返回重试
              </Text>
              <div style={{ textAlign: "center" }}>
                <Button onClick={() => navigate("/")} type="primary">
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

    if (question.allow_custom && answer === "CUSTOM") {
      return customAnswers[question.id] && customAnswers[question.id].trim();
    }

    return !!answer;
  };

  const handleAnswer = (questionId, value) => {
    setAnswers({
      ...answers,
      [questionId]: value,
    });

    if (value !== "CUSTOM") {
      const newCustomAnswers = { ...customAnswers };
      delete newCustomAnswers[questionId];
      setCustomAnswers(newCustomAnswers);
    }
  };

  const handleCustomAnswer = (questionId, value) => {
    setCustomAnswers({
      ...customAnswers,
      [questionId]: value,
    });
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setIsShowingAdditionalRequirements(true);
    }
  };

  // 轮询获取需求字段
  const pollRequirementFields = async () => {
    const maxAttempts = 60;
    const interval = 3000;
    let attempts = 0;

    // 初始化进度状态
    setLoadingProgress(20);
    setCurrentLoadingStep("正在分析您的需求...");

    const poll = async () => {
      attempts++;
      
      // 更新进度条和步骤描述
      const progressValue = Math.min(20 + (attempts / maxAttempts) * 70, 90);
      setLoadingProgress(Math.floor(progressValue));
      
      if (attempts <= 20) {
        setCurrentLoadingStep("正在分析您的需求...");
      } else if (attempts <= 40) {
        setCurrentLoadingStep("正在生成个性化方案...");
      } else {
        setCurrentLoadingStep("正在完善应用细节...");
      }
      
      setLoadingText(`正在生成需求表单... (${attempts}/${maxAttempts})`);

      try {
        const result = await request.get(`/api/requirement/fields/${threadId}`);
        console.log("轮询字段结果:", result);

        // 200状态码且data不为null，表示成功
        if (result.code === 0 && result.data !== null) {
          setLoadingProgress(100);
          setCurrentLoadingStep("生成完成！");
          
          // 短暂显示完成状态
          setTimeout(() => {
            navigate("/requirement-form", {
              state: {
                userInput: userInput,
                threadId: threadId,
                requirementData: result.data,
              },
            });
          }, 500);
          return;
        }
      } catch (error) {
        // 400状态码或其他错误都当作"还未准备好"处理
        console.log(
          "数据还未准备好，继续轮询...",
          error.status || error.message,
        );
      }

      // 继续轮询或超时处理
      if (attempts < maxAttempts) {
        setTimeout(poll, interval);
      } else {
        setIsComplete(false);
        setIsSubmitting(false);
        setCurrentLoadingStep("生成超时，请重试");
      }
    };

    poll();
  };

  const submitAnswers = async () => {
    setIsSubmitting(true);
    setLoadingProgress(0);
    setCurrentLoadingStep("正在提交您的答案...");

    try {
      const answersArray = [];

      questions.forEach((question) => {
        const answer = answers[question.id];
        if (answer === "CUSTOM" && customAnswers[question.id]) {
          answersArray.push({
            question_id: question.id,
            custom_input: customAnswers[question.id].trim(),
          });
        } else if (answer) {
          answersArray.push({
            question_id: question.id,
            selected_option: answer,
          });
        }
      });

      const submissionData = {
        answers: answersArray,
        additional_requirements: additionalRequirements.trim() || null,
      };

      console.log("提交的答案数据:", submissionData);
      setLoadingProgress(10);
      setCurrentLoadingStep("正在处理您的答案...");

      // 调用API提交答案
      const result = await request.post(
        `/api/requirement/submit-answers/${threadId}`,
        submissionData,
      );

      if (result.code === 0) {
        setIsComplete(true);
        setCurrentLoadingStep("答案提交成功，开始生成方案...");

        // 开始轮询需求字段
        await pollRequirementFields();
      } else {
        throw new Error(result.message || "提交失败");
      }
    } catch (error) {
      console.error("提交答案失败:", error);
      setIsSubmitting(false);
      setLoadingProgress(0);
      setCurrentLoadingStep("提交失败，请重试");
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
    setAdditionalRequirements("");
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
        <div className="questionnaire-container" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: '20px'
        }}>
          <Card className="question-card" style={{
            width: '100%',
            maxWidth: '700px',
            borderRadius: '24px',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.08)',
            border: '1px solid rgba(226, 232, 240, 0.6)',
            backdropFilter: 'blur(20px)',
            background: 'rgba(255, 255, 255, 0.95)'
          }}>
            <div className="completion-card" style={{
              textAlign: 'center',
              padding: '40px 32px'
            }}>
              {/* 返回按钮 */}
              <div style={{
                display: 'flex',
                justifyContent: 'flex-start',
                marginBottom: '20px',
                paddingBottom: '16px',
                borderBottom: '1px solid rgba(226, 232, 240, 0.5)'
              }}>
                <Button
                  icon={<IconArrowLeft />}
                  theme="borderless"
                  onClick={() => navigate("/")}
                  style={{
                    background: 'rgba(248, 250, 252, 0.8)',
                    border: '1px solid rgba(203, 213, 224, 0.6)',
                    borderRadius: '12px',
                    color: '#475569',
                    fontWeight: '500',
                    padding: '8px 16px',
                    transition: 'all 0.3s ease'
                  }}
                >
                  返回首页
                </Button>
              </div>

              <div className="generating-icon questionnaire-loading-animation" style={{
                marginBottom: '32px'
              }}>
                <Spin size="large" />
              </div>

              <div style={{
                marginBottom: '32px'
              }}>
                <Title
                  heading={3}
                  style={{
                    textAlign: "center",
                    margin: "0 0 32px 0",
                    color: "#1a202c",
                    fontSize: "24px",
                    fontWeight: "700",
                    background: "linear-gradient(135deg, #1a202c 0%, #374151 100%)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    backgroundClip: "text",
                  }}
                >
                  正在生成需求表单
                </Title>

                <div className="questionnaire-progress-container" style={{
                  maxWidth: '500px',
                  margin: '0 auto'
                }}>
                  <Progress
                    percent={Math.floor(loadingProgress)}
                    showInfo={true}
                    format={(percent) => `${Math.floor(percent)}%`}
                    stroke="#374151"
                    size="large"
                    style={{ 
                      marginBottom: "16px",
                    }}
                  />
                  <Text
                    style={{
                      textAlign: "center",
                      fontSize: "16px",
                      color: "#666",
                      display: "block",
                      minHeight: "24px",
                      lineHeight: "1.5",
                    }}
                  >
                    {currentLoadingStep}
                  </Text>

                  {/* 显示处理状态 */}
                  <div style={{ textAlign: "center", marginTop: "16px" }}>
                    <Text 
                      className="questionnaire-status-indicator"
                      style={{ 
                        fontSize: "14px", 
                        color: "#6b7280",
                        background: "rgba(243, 244, 246, 0.8)",
                        padding: "8px 16px",
                        borderRadius: "20px",
                        border: "1px solid #e5e7eb",
                        display: "inline-block",
                        transition: "all 0.3s ease"
                      }}>
                      需求表单状态:{" "}
                      <span style={{
                        color: loadingProgress === 100 ? "#10b981" : "#f59e0b",
                        fontWeight: "600"
                      }}>
                        {loadingProgress === 100 ? "已完成" : "处理中"}
                      </span>
                    </Text>
                  </div>
                </div>
              </div>

              <div style={{
                padding: '24px',
                background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                borderRadius: '16px',
                border: '1px solid #e2e8f0',
                marginTop: '20px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)'
              }}>
                <Text
                  type="secondary"
                  style={{
                    fontSize: "14px",
                    textAlign: "center",
                    display: "block",
                  }}
                >
                  我们正在根据您的需求和答案创建定制化的应用方案，请稍候片刻
                </Text>
              </div>
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
              onClick={() => navigate("/")}
              style={{ marginBottom: "8px", color: "#000000" }}
            >
              返回首页
            </Button>

            <div className="user-input-summary">
              <Text type="secondary" size="large">
                距离您的专属应用更近一步。请回答几个核心问题，让我们更好地为您定制解决方案
              </Text>
              <Text
                style={{
                  display: "block",
                  marginTop: "4px",
                  padding: "8px 12px",
                  background: "#f8fafc",
                  borderRadius: "8px",
                  fontSize: "14px",
                }}
              >
                {userInput}
              </Text>
            </div>
          </div>

          <Card className="question-card">
            <div className="progress-section">
              <div className="progress-info">
                <Text style={{ fontSize: "14px", color: "#666" }}>
                  额外需求 (可选)
                </Text>
                <Text style={{ fontSize: "14px", color: "#666" }}>
                  100% 完成
                </Text>
              </div>
              <Progress
                percent={100}
                showInfo={false}
                stroke="#374151"
                style={{ marginTop: "8px" }}
              />
            </div>

            <div className="question-content">
              <Title
                heading={3}
                style={{ marginBottom: "24px", color: "#1a202c" }}
              >
                是否有其他额外需求？
              </Title>

              <div className="additional-requirements-container">
                <Text
                  type="secondary"
                  style={{ marginBottom: "16px", display: "block" }}
                >
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
                    borderRadius: "12px",
                    border: "1px solid #e2e8f0",
                  }}
                />

                <Text
                  type="tertiary"
                  size="small"
                  style={{ marginTop: "8px", display: "block" }}
                >
                  {additionalRequirements.length}/500 字符
                </Text>
              </div>
            </div>

            <div className="question-navigation">
              <Button
                icon={<IconArrowLeft />}
                onClick={handlePrevious}
                disabled={isSubmitting}
                style={{ color: "#000000" }}
              >
                上一题
              </Button>

              <Space>
                <Button
                  type="primary"
                  onClick={handleSubmitWithAdditionalRequirements}
                  loading={isSubmitting}
                  style={{ color: "#000000" }}
                >
                  {isSubmitting ? "提交中..." : "完成提交"}
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
            onClick={() => navigate("/")}
            style={{ marginBottom: "8px", color: "#000000" }}
          >
            返回首页
          </Button>

          <div className="user-input-summary">
            <Text type="secondary" size="large" style={{ color: "#000000" }}>
              距离您的专属应用更近一步。请回答几个核心问题，让我们更好地为您定制解决方案
            </Text>
            <Text
              style={{
                display: "block",
                marginTop: "8px",
                padding: "8px 12px",
                background: "#f8fafc",
                borderRadius: "8px",
              }}
            >
              {userInput}
            </Text>
          </div>
        </div>

        <Card className="question-card">
          <div className="progress-section">
            <div className="progress-info">
              <Text style={{ fontSize: "14px", color: "#666" }}>
                问题 {currentQuestion + 1} / {questions.length}
              </Text>
              <Text style={{ fontSize: "14px", color: "#666" }}>
                {Math.round(progress)}% 完成
              </Text>
            </div>
            <Progress
              percent={progress}
              showInfo={false}
              stroke="#374151"
              style={{ marginTop: "8px" }}
            />
          </div>

          <div className="question-content">
            <Title
              heading={3}
              style={{ marginBottom: "24px", color: "#1a202c" }}
            >
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

                {question.allow_custom && (
                  <div className="option-item custom-option">
                    <Radio value="CUSTOM">
                      <div className="option-content">
                        <div className="option-label">其他（请说明）</div>
                      </div>
                    </Radio>
                    {answers[question.id] === "CUSTOM" && (
                      <div className="custom-input-container">
                        <Input
                          placeholder="请输入您的具体需求..."
                          value={customAnswers[question.id] || ""}
                          onChange={(value) =>
                            handleCustomAnswer(question.id, value)
                          }
                          maxLength={200}
                          showClear
                          style={{ marginTop: "12px", marginLeft: "32px" }}
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
              style={{
                visibility: currentQuestion === 0 ? "hidden" : "visible",
                color: "#000000",
              }}
            >
              上一题
            </Button>

            <Button
              type="primary"
              icon={<IconArrowRight />}
              iconPosition="right"
              onClick={handleNext}
              disabled={!isCurrentAnswered()}
              style={{ color: "#000000" }}
            >
              {currentQuestion === questions.length - 1 ? "下一步" : "下一题"}
            </Button>
          </div>
        </Card>
      </div>
    </Content>
  );
}

export default Questionnaire;
