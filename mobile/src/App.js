/**
 * CyberSafe Mobile App - Main Application
 */

import React, {useState, useEffect} from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {StatusBar, useColorScheme} from 'react-native';

// Screens
import DashboardScreen from './screens/DashboardScreen';
import PacketsScreen from './screens/PacketsScreen';
import ThreatsScreen from './screens/ThreatsScreen';
import PortsScreen from './screens/PortsScreen';
import SettingsScreen from './screens/SettingsScreen';

// API
import {checkConnection} from './api/client';

const Tab = createBottomTabNavigator();

const App = () => {
  const [isConnected, setIsConnected] = useState(false);
  const isDarkMode = useColorScheme() === 'dark';

  useEffect(() => {
    // Check backend connection
    checkConnection()
      .then(() => setIsConnected(true))
      .catch(() => setIsConnected(false));
  }, []);

  const theme = {
    dark: isDarkMode,
    colors: {
      primary: '#2196F3',
      background: isDarkMode ? '#1a1a1a' : '#f5f5f5',
      card: isDarkMode ? '#2d2d2d' : '#ffffff',
      text: isDarkMode ? '#ffffff' : '#212121',
      border: isDarkMode ? '#3d3d3d' : '#e0e0e0',
      notification: '#FF9800',
    },
  };

  return (
    <NavigationContainer theme={theme}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={theme.colors.background}
      />
      
      <Tab.Navigator
        screenOptions={({route}) => ({
          tabBarIcon: ({focused, color, size}) => {
            let iconName;

            switch (route.name) {
              case 'Dashboard':
                iconName = 'dashboard';
                break;
              case 'Packets':
                iconName = 'wifi-tethering';
                break;
              case 'Threats':
                iconName = 'security';
                break;
              case 'Ports':
                iconName = 'router';
                break;
              case 'Settings':
                iconName = 'settings';
                break;
              default:
                iconName = 'help';
            }

            return <Icon name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#2196F3',
          tabBarInactiveTintColor: '#808080',
          tabBarStyle: {
            backgroundColor: theme.colors.card,
            borderTopColor: theme.colors.border,
          },
          headerStyle: {
            backgroundColor: theme.colors.card,
          },
          headerTintColor: theme.colors.text,
          headerRight: () => (
            <Icon
              name={isConnected ? 'cloud-done' : 'cloud-off'}
              size={24}
              color={isConnected ? '#4CAF50' : '#F44336'}
              style={{marginRight: 16}}
            />
          ),
        })}>
        
        <Tab.Screen 
          name="Dashboard" 
          component={DashboardScreen}
          options={{title: 'CyberSafe Monitor'}}
        />
        <Tab.Screen 
          name="Packets" 
          component={PacketsScreen}
          options={{title: 'Network Packets'}}
        />
        <Tab.Screen 
          name="Threats" 
          component={ThreatsScreen}
          options={{title: 'Threats'}}
        />
        <Tab.Screen 
          name="Ports" 
          component={PortsScreen}
          options={{title: 'Ports & Connections'}}
        />
        <Tab.Screen 
          name="Settings" 
          component={SettingsScreen}
          options={{title: 'Settings'}}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
};

export default App;
