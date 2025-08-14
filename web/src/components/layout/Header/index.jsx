import React from 'react';
import { Layout, Button, Typography, Space, Avatar, ButtonGroup } from '@douyinfe/semi-ui';
import { IconBell, IconSun, IconMoon, IconSetting, IconBolt } from '@douyinfe/semi-icons';

const { Header: SemiHeader } = Layout;
const { Title } = Typography;

function Header({ darkMode, setDarkMode }) {
  return (
    <SemiHeader className="top-header">
      <div className="header-content">
        <div className="logo-section">
          <Avatar 
            size="default" 
            shape="square"
            style={{ marginRight: 12 }}
            src="/logo.png"
          />
          <Title heading={3} style={{ margin: 0, color: '#2d3748' }}>
            Agentify
          </Title>
        </div>
        
        <Space>
          <Button style={{ color: '#5c5c5cff', borderRadius: 10 }} icon={<IconBell />} />
          <Button 
            style={{ color: '#5c5c5cff', borderRadius: 10 }}
            icon={darkMode ? <IconSun /> : <IconMoon />}
            onClick={() => setDarkMode(!darkMode)}
          />
          <Button style={{ color: '#5c5c5cff', borderRadius: 10 }} icon={<IconSetting />} />
          <ButtonGroup size='default' style={{ margin: 4, borderRadius: 10, overflow: 'hidden' }}>
            <Button disabled style={{ color: '#5c5c5cff' }}><IconBolt />3</Button>
            <Button>Upgrade</Button>
          </ButtonGroup>
          <Avatar size="small" style={{ backgroundColor: '#f56565' }}>
            CJH
          </Avatar>
        </Space>
      </div>
    </SemiHeader>
  );
}

export default Header;