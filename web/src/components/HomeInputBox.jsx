import { useState } from 'react';
import { Card, TextArea, Button, Space } from '@douyinfe/semi-ui';
import { IconPlus, IconGlobeStroke, IconArrowUp } from '@douyinfe/semi-icons';


function HomeInputBox() {
  const [text, setText] = useState('');

  const suggestionTags = ['Branding', 'Posters', 'Ads', 'Character Design', 'Videos'];

  return (
    <div className="creative-input__wrapper">
      
      <h2 className="creative-input__title">
        What are we creating today, jh c?
      </h2>

      <Card
        className="creative-input__card"
        bodyStyle={{ padding: '16px 24px' }}
      >
        <TextArea
          placeholder="Start with a creative idea or task"
          value={text}
          onChange={(value) => setText(value)}
          autosize={{ minRows: 3, maxRows: 8 }}
          className="creative-input__textarea"
        />
        
        <div className="creative-input__toolbar">
          <Space>
            <Button
              theme="borderless"
              type="tertiary"
              icon={<IconPlus />}
            />
            <Button
              theme="borderless"
              type="tertiary"
              icon={<IconWorld />}
            />
          </Space>

          <Button
            shape="circle"
            icon={<IconArrowUp />}
            className="creative-input__submit-btn"
          />
        </div>
      </Card>

      {/* 使用 Semi-Design 的 Tag 组件 */}
      <div className="creative-input__tags-container">
        {suggestionTags.map(tag => (
          <Tag 
            key={tag}
            size="large"
            className="creative-input__tag"
          >
            {tag}
          </Tag>
        ))}
      </div>
    </div>
  );
}

export default HomeInputBox;