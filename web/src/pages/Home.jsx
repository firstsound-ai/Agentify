import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Layout,
  Button,
  Typography,
  TextArea,
  Progress,
  Modal,
} from "@douyinfe/semi-ui";
import {
  IconFlipHorizontal,
  IconCrown,
  IconSearch,
  IconDesktop,
  IconFile,
  IconCloud,
} from "@douyinfe/semi-icons";
import "./Home.css";
import request from "../utils/request";

const { Content } = Layout;
const { Title, Text } = Typography;

const AnimatedTitle = ({ text, style }) => {
  const [visibleChars, setVisibleChars] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setVisibleChars((prev) => {
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
      {text.split("").map((char, index) => (
        <span
          key={index}
          className={`animated-char ${index < visibleChars ? "visible" : ""}`}
          style={{
            animationDelay: `${index * 0.15}s`,
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
  const [mainInput, setMainInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("正在创建需求...");
  const [progress, setProgress] = useState(0);
  const [showLoadingModal, setShowLoadingModal] = useState(false);
  const [isCancelled, setIsCancelled] = useState(false);
  const [activeTab, setActiveTab] = useState("featured");

  const pollTimer = useRef(null);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (pollTimer.current) {
        clearTimeout(pollTimer.current);
      }
    };
  }, []);

  // 取消生成
  const handleCancelLoading = () => {
    setIsCancelled(true);
    if (pollTimer.current) {
      clearTimeout(pollTimer.current);
    }
    setShowLoadingModal(false);
    setIsLoading(false);
    setProgress(0);
    setIsCancelled(false);
  };

  // 直接设置进度
  const updateProgress = (newProgress) => {
    setProgress(newProgress);
  };

  // 创建需求并获取thread_id的函数
  const createRequirement = async (userInput) => {
    try {
      const result = await request.post("/api/requirement/create", {
        initial_requirement: userInput,
      });

      if (result.code === 0) {
        return result.data.thread_id;
      } else {
        throw new Error(result.message || "创建需求失败");
      }
    } catch (error) {
      console.error("创建需求失败:", error);
      throw error;
    }
  };

  // 获取需求状态的函数
  const getRequirementStatus = async (threadId) => {
    try {
      const result = await request.get(`/api/requirement/status/${threadId}`);
      return result;
    } catch (error) {
      console.error("获取需求状态失败:", error);
      throw error;
    }
  };

  // 轮询获取状态直到问卷生成完成
  const pollRequirementStatus = async (threadId, userInput) => {
    const maxAttempts = 30; // 最多轮询30次
    const interval = 2000; // 每2秒轮询一次
    let attempts = 0;

    const poll = async () => {
      if (isCancelled) return;

      try {
        attempts++;
        // 直接计算并设置进度
        const pollProgress = (attempts / maxAttempts) * 100;
        updateProgress(Math.round(Math.min(pollProgress, 95)));
        setLoadingText(`正在生成需求问卷...`);

        const statusResult = await getRequirementStatus(threadId);
        console.log("轮询状态结果:", statusResult);

        if (isCancelled) return;

        if (
          statusResult.data.status === "waiting_for_answers" &&
          statusResult.data.questionnaire
        ) {
          // 问卷已生成，设置为100%
          updateProgress(100);
          setLoadingText("问卷生成完成，正在跳转...");

          // 短暂延迟让用户看到完成状态
          setTimeout(() => {
            if (!isCancelled) {
              setShowLoadingModal(false);
              setIsLoading(false);
              setProgress(0);
              // 跳转到问卷页面
              navigate("/questionnaire", {
                state: {
                  userInput: userInput,
                  threadId: threadId,
                  questionnaire: statusResult.data.questionnaire,
                },
              });
            }
          }, 1500);
          return;
        } else if (statusResult.data.status === "pending") {
          // 还在处理中，继续轮询
          if (attempts < maxAttempts && !isCancelled) {
            pollTimer.current = setTimeout(poll, interval);
          } else if (!isCancelled) {
            throw new Error("生成问卷超时，请重试");
          }
        } else if (statusResult.data.error) {
          // 有错误
          throw new Error(statusResult.data.error);
        } else {
          // 其他状态，继续轮询
          if (attempts < maxAttempts && !isCancelled) {
            pollTimer.current = setTimeout(poll, interval);
          } else if (!isCancelled) {
            throw new Error("生成问卷超时，请重试");
          }
        }
      } catch (error) {
        if (!isCancelled) {
          console.error("轮询失败:", error);
          setShowLoadingModal(false);
          setIsLoading(false);
          setProgress(0);
        }
      }
    };

    // 开始轮询
    poll();
  };

  const handleMainSubmit = async () => {
    if (!mainInput.trim()) return;

    setIsLoading(true);
    setShowLoadingModal(true);
    setIsCancelled(false);
    setProgress(0);
    setLoadingText("正在创建需求...");

    try {
      // 第一步：设置初始进度
      updateProgress(1);

      // 第二步：创建需求并获取thread_id
      setLoadingText("正在创建需求...");
      const threadId = await createRequirement(mainInput.trim());

      if (isCancelled) return;

      // 第三步：开始轮询状态
      updateProgress(30);
      setLoadingText("需求创建成功，开始生成问卷...");
      await pollRequirementStatus(threadId, mainInput.trim());
    } catch (error) {
      if (!isCancelled) {
        console.error("处理失败:", error);
        setShowLoadingModal(false);
        setIsLoading(false);
        setProgress(0);
      }
    }
  };

  const handleMainInputKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleMainSubmit();
    }
  };

  // 快捷提示词数据
  const promptCategories = {
    featured: {
      name: "精选",
      prompts: [
        {
          title: "智能文档助手",
          description: "帮我创建一个能够自动整理和总结文档的AI助手",
          content: "创建一个智能文档助手，能够自动分析、整理和总结各类文档内容",
        },
        {
          title: "个人日程管理",
          description: "设计一个智能日程规划和时间管理系统",
          content:
            "设计一个个人日程管理应用，包含智能提醒、优先级排序和时间统计功能",
        },
        {
          title: "创意写作工具",
          description: "构建一个支持多种文体的AI写作助手",
          content:
            "构建一个创意写作工具，支持小说、诗歌、剧本等多种文体的创作辅助",
        },
        {
          title: "智能客服系统",
          description: "开发24小时在线的智能客户服务机器人",
          content:
            "开发一个智能客服系统，能够理解用户问题、提供准确答案并无缝转接人工客服",
        },
      ],
    },
    research: {
      name: "研究",
      prompts: [
        {
          title: "学术论文分析",
          description: "开发能够解析和总结学术论文的研究工具",
          content:
            "开发一个学术论文分析工具，能够自动提取关键信息、分析研究方法和总结结论",
        },
        {
          title: "数据挖掘平台",
          description: "创建用于大数据分析和模式识别的平台",
          content: "创建一个数据挖掘分析平台，支持多维度数据探索和智能模式识别",
        },
        {
          title: "文献综述助手",
          description: "构建自动化文献搜索和综述生成工具",
          content:
            "构建一个文献综述助手，能够自动搜索相关文献并生成结构化综述报告",
        },
        {
          title: "实验数据管理",
          description: "设计科研实验数据收集和分析系统",
          content:
            "设计一个实验数据管理系统，支持数据采集、处理、分析和可视化展示",
        },
      ],
    },
    productivity: {
      name: "生产力",
      prompts: [
        {
          title: "任务自动化",
          description: "设计智能任务分配和进度跟踪系统",
          content:
            "设计一个任务自动化管理系统，包含智能分配、进度跟踪和效率分析功能",
        },
        {
          title: "会议纪要生成",
          description: "开发自动生成会议总结和行动项的工具",
          content:
            "开发一个会议纪要自动生成工具，能够实时记录、总结要点并提取行动项",
        },
        {
          title: "邮件智能处理",
          description: "创建邮件自动分类和回复建议系统",
          content:
            "创建一个邮件智能处理系统，支持自动分类、优先级标记和回复建议生成",
        },
        {
          title: "知识库管理",
          description: "构建企业知识共享和检索平台",
          content:
            "构建一个企业知识库管理系统，支持文档自动分类、智能搜索和知识推荐",
        },
      ],
    },
    education: {
      name: "教育",
      prompts: [
        {
          title: "个性化学习路径",
          description: "构建适应性学习和知识图谱系统",
          content:
            "构建一个个性化学习平台，根据学习者特点生成定制化学习路径和内容推荐",
        },
        {
          title: "智能题库生成",
          description: "开发自动生成练习题和测验的教学工具",
          content:
            "开发一个智能题库系统，能够根据知识点自动生成不同难度的练习题和测验",
        },
        {
          title: "课程内容助手",
          description: "创建课程设计和教学内容生成工具",
          content:
            "创建一个课程内容助手，帮助教师设计课程结构、生成教学材料和评估方案",
        },
        {
          title: "学习进度跟踪",
          description: "开发学生学习行为分析和成绩预测系统",
          content:
            "开发一个学习进度跟踪系统，分析学生学习行为、预测学习效果并提供改进建议",
        },
      ],
    },
    data: {
      name: "数据",
      prompts: [
        {
          title: "可视化看板",
          description: "构建交互式数据可视化和仪表板系统",
          content: "构建一个数据可视化看板，支持多数据源接入和交互式图表展示",
        },
        {
          title: "预测分析模型",
          description: "开发业务预测和趋势分析工具",
          content:
            "开发一个预测分析系统，基于历史数据进行趋势预测和业务洞察分析",
        },
        {
          title: "报表自动化",
          description: "创建定期报表生成和分发系统",
          content:
            "创建一个报表自动化系统，支持定时生成、格式化和自动分发各类业务报表",
        },
        {
          title: "数据质量监控",
          description: "建立数据质量检测和异常告警机制",
          content:
            "建立一个数据质量监控系统，实时检测数据异常、评估数据质量并自动生成告警",
        },
      ],
    },
  };

  return (
    <Content className="chat-content">
      <div className="chat-container">
        {/* 主要输入区域 */}
        <div className="main-input-section">
          <div className="welcome-header">
            <div className="brand-section">
              <div className="logo-container">
                <img
                  src="/logo.png"
                  alt="Agentify Logo"
                  className="brand-logo"
                />
              </div>
              <div className="text-container">
                <AnimatedTitle
                  text="Agent，聊出来"
                  style={{
                    fontSize: "56px",
                    margin: 0,
                    textAlign: "center",
                    color: "#000000",
                    lineHeight: "1.2",
                  }}
                />
                <Text
                  type="secondary"
                  style={{
                    fontSize: "16px",
                    marginTop: "8px",
                    display: "block",
                    textAlign: "left",
                  }}
                >
                  告别复杂配置，用对话构建你的Agent
                </Text>
              </div>
            </div>
          </div>

          <div className="simple-input-section">
            <TextArea
              placeholder="告诉Agentify你的任务，例如：我需要写一份AI技术的发展报告，包含市场分析、技术趋势、未来展望..."
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
                {isLoading ? loadingText : "开始创作"}
              </Button>
            </div>
          </div>

          <div style={{ marginTop: "24px" }}>
            <div className="tab-buttons-container">
              {Object.entries(promptCategories).map(([key, category]) => {
                // 为不同类别定义图标
                const getIcon = (categoryKey) => {
                  switch (categoryKey) {
                    case "featured":
                      return <IconCrown />;
                    case "research":
                      return <IconSearch />;
                    case "productivity":
                      return <IconDesktop />;
                    case "education":
                      return <IconFile />;
                    case "data":
                      return <IconCloud />;
                    default:
                      return <IconCrown />;
                  }
                };

                return (
                  <Button
                    icon={getIcon(key)}
                    key={key}
                    className={`tab-button ${
                      activeTab === key ? "active" : ""
                    }`}
                    onClick={() => {
                      setActiveTab(key);
                    }}
                    disabled={isLoading}
                    type="secondary"
                  >
                    {category.name}
                  </Button>
                );
              })}
            </div>

            {/* Tab 内容 */}
            <div className="tab-content">
              <div className="prompts-grid">
                {promptCategories[activeTab].prompts.map((prompt, index) => (
                  <div
                    key={index}
                    className={`prompt-card ${isLoading ? "disabled" : ""}`}
                    onClick={() => !isLoading && setMainInput(prompt.content)}
                  >
                    <div className="prompt-card-title">{prompt.title}</div>
                    <div className="prompt-card-description">
                      {prompt.description}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 加载进度模态框 */}
        <Modal
          title="正在处理您的需求"
          visible={showLoadingModal}
          footer={null}
          closable={false}
          width={400}
          centered
          maskClosable={false}
        >
          <div style={{ textAlign: "center", padding: "20px 0" }}>
            <Progress
              percent={Math.round(progress)}
              showInfo={false}
              stroke="#000000"
              style={{ marginBottom: "10px" }}
              aria-label="问卷生成进度"
            />
            <Typography.Text type="secondary" style={{ fontSize: "14px" }}>
              {loadingText}
            </Typography.Text>
            <div
              style={{ marginTop: "16px", color: "#6b7280", fontSize: "12px" }}
            >
              请稍候，我们正在为您精心准备个性化问卷...
            </div>
            <div style={{ marginTop: "24px" }}>
              <Button
                type="tertiary"
                theme="borderless"
                onClick={handleCancelLoading}
                style={{
                  color: "#ef4444",
                  border: "1px solid #fecaca",
                  borderRadius: "6px",
                  padding: "6px 16px",
                  fontSize: "13px",
                }}
              >
                取消生成
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </Content>
  );
}

export default Home;
