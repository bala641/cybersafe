/**
 * Settings Screen - App configuration and about
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SettingsScreen = () => {
  const [apiUrl, setApiUrl] = useState('http://192.168.1.100:5000');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [notifications, setNotifications] = useState(true);

  const saveSettings = async () => {
    try {
      await AsyncStorage.setItem('api_url', apiUrl);
      await AsyncStorage.setItem('auto_refresh', autoRefresh.toString());
      await AsyncStorage.setItem('notifications', notifications.toString());
      Alert.alert('Success', 'Settings saved successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to save settings');
    }
  };

  const resetSettings = () => {
    Alert.alert(
      'Reset Settings',
      'Are you sure you want to reset all settings to default?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            setApiUrl('http://192.168.1.100:5000');
            setAutoRefresh(true);
            setNotifications(true);
            Alert.alert('Success', 'Settings reset to default');
          },
        },
      ]
    );
  };

  const SettingItem = ({icon, label, value, onPress, type = 'toggle'}) => (
    <TouchableOpacity style={styles.settingItem} onPress={onPress}>
      <View style={styles.settingLeft}>
        <Icon name={icon} size={24} color="#2196F3" />
        <Text style={styles.settingLabel}>{label}</Text>
      </View>
      {type === 'toggle' && (
        <View style={[styles.toggle, value && styles.toggleActive]}>
          <View style={[styles.toggleThumb, value && styles.toggleThumbActive]} />
        </View>
      )}
      {type === 'arrow' && (
        <Icon name="chevron-right" size={24} color="#757575" />
      )}
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Connection Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Connection</Text>
        
        <View style={styles.card}>
          <Text style={styles.inputLabel}>Backend API URL</Text>
          <TextInput
            style={styles.input}
            value={apiUrl}
            onChangeText={setApiUrl}
            placeholder="http://192.168.1.100:5000"
            placeholderTextColor="#757575"
            keyboardType="url"
            autoCapitalize="none"
          />
          <Text style={styles.inputHint}>
            Enter the IP address or hostname of your CyberSafe backend
          </Text>
        </View>
      </View>

      {/* App Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Application</Text>
        
        <View style={styles.card}>
          <SettingItem
            icon="autorenew"
            label="Auto Refresh"
            value={autoRefresh}
            onPress={() => setAutoRefresh(!autoRefresh)}
          />
          
          <View style={styles.divider} />
          
          <SettingItem
            icon="notifications"
            label="Threat Notifications"
            value={notifications}
            onPress={() => setNotifications(!notifications)}
          />
        </View>
      </View>

      {/* Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Actions</Text>
        
        <View style={styles.card}>
          <TouchableOpacity style={styles.actionButton} onPress={saveSettings}>
            <Icon name="save" size={24} color="#4CAF50" />
            <Text style={[styles.actionText, {color: '#4CAF50'}]}>
              Save Settings
            </Text>
          </TouchableOpacity>
          
          <View style={styles.divider} />
          
          <TouchableOpacity style={styles.actionButton} onPress={resetSettings}>
            <Icon name="refresh" size={24} color="#FF9800" />
            <Text style={[styles.actionText, {color: '#FF9800'}]}>
              Reset to Default
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* About */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        
        <View style={styles.card}>
          <View style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Version</Text>
            <Text style={styles.aboutValue}>1.0.0</Text>
          </View>
          
          <View style={styles.divider} />
          
          <View style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Build</Text>
            <Text style={styles.aboutValue}>2026.10.19</Text>
          </View>
          
          <View style={styles.divider} />
          
          <TouchableOpacity style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>GitHub</Text>
            <Icon name="open-in-new" size={20} color="#2196F3" />
          </TouchableOpacity>
          
          <View style={styles.divider} />
          
          <TouchableOpacity style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Documentation</Text>
            <Icon name="open-in-new" size={20} color="#2196F3" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Icon name="security" size={32} color="#2196F3" />
        <Text style={styles.footerTitle}>CyberSafe Network Monitor</Text>
        <Text style={styles.footerText}>
          Professional network traffic monitoring and threat detection
        </Text>
        <Text style={styles.footerCopyright}>
          © 2026 CyberSafe. All rights reserved.
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  section: {
    marginTop: 20,
  },
  sectionTitle: {
    color: '#2196F3',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 20,
    marginBottom: 10,
    textTransform: 'uppercase',
  },
  card: {
    backgroundColor: '#2d2d2d',
    marginHorizontal: 10,
    borderRadius: 8,
    overflow: 'hidden',
  },
  inputLabel: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
    margin: 15,
    marginBottom: 10,
  },
  input: {
    backgroundColor: '#3d3d3d',
    color: '#ffffff',
    fontSize: 14,
    padding: 15,
    marginHorizontal: 15,
    borderRadius: 8,
    fontFamily: 'monospace',
  },
  inputHint: {
    color: '#757575',
    fontSize: 12,
    margin: 15,
    marginTop: 10,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingLabel: {
    color: '#ffffff',
    fontSize: 14,
    marginLeft: 15,
  },
  toggle: {
    width: 50,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#3d3d3d',
    padding: 2,
    justifyContent: 'center',
  },
  toggleActive: {
    backgroundColor: '#2196F3',
  },
  toggleThumb: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#ffffff',
  },
  toggleThumbActive: {
    alignSelf: 'flex-end',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
  },
  actionText: {
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 15,
  },
  divider: {
    height: 1,
    backgroundColor: '#3d3d3d',
    marginLeft: 55,
  },
  aboutItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
  },
  aboutLabel: {
    color: '#ffffff',
    fontSize: 14,
  },
  aboutValue: {
    color: '#b0b0b0',
    fontSize: 14,
    fontFamily: 'monospace',
  },
  footer: {
    alignItems: 'center',
    padding: 30,
    marginTop: 20,
  },
  footerTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 10,
  },
  footerText: {
    color: '#b0b0b0',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 10,
    marginHorizontal: 30,
  },
  footerCopyright: {
    color: '#757575',
    fontSize: 11,
    marginTop: 20,
  },
});

export default SettingsScreen;
