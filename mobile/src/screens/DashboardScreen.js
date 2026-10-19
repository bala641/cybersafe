/**
 * Dashboard Screen - Overview of network monitoring
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {getStatus, getStats, startMonitoring, stopMonitoring} from '../api/client';
import CONFIG from '../config';

const DashboardScreen = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [monitoring, setMonitoring] = useState(false);
  const [stats, setStats] = useState({
    capture: {},
    threats: {},
    ports: {},
    network_io: {},
  });

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, CONFIG.refreshIntervals.dashboard);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statusData, statsData] = await Promise.all([
        getStatus(),
        getStats(),
      ]);
      
      setMonitoring(statusData.monitoring_active);
      setStats(statsData);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const toggleMonitoring = async () => {
    try {
      if (monitoring) {
        await stopMonitoring();
      } else {
        await startMonitoring();
      }
      setMonitoring(!monitoring);
    } catch (error) {
      console.error('Error toggling monitoring:', error);
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  const captureStats = stats.capture || {};
  const threatStats = stats.threats || {};
  const portStats = stats.ports || {};
  const ioStats = stats.network_io || {};

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={() => {
          setRefreshing(true);
          loadData();
        }} />
      }>
      
      {/* Status Card */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Icon 
            name={monitoring ? 'play-circle-filled' : 'pause-circle-filled'} 
            size={32} 
            color={monitoring ? '#4CAF50' : '#F44336'} 
          />
          <Text style={styles.cardTitle}>
            {monitoring ? 'Monitoring Active' : 'Monitoring Inactive'}
          </Text>
        </View>
        
        <TouchableOpacity
          style={[styles.button, monitoring ? styles.stopButton : styles.startButton]}
          onPress={toggleMonitoring}>
          <Text style={styles.buttonText}>
            {monitoring ? 'Stop Monitoring' : 'Start Monitoring'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Statistics Grid */}
      <View style={styles.statsGrid}>
        <StatCard
          icon="wifi-tethering"
          title="Total Packets"
          value={captureStats.total_packets || 0}
          color="#2196F3"
        />
        <StatCard
          icon="security"
          title="Threats"
          value={threatStats.total_threats || 0}
          color="#F44336"
        />
        <StatCard
          icon="router"
          title="Active Ports"
          value={portStats.listening_ports || 0}
          color="#FF9800"
        />
        <StatCard
          icon="swap-vert"
          title="Data Rate"
          value={`${((captureStats.bytes_per_second || 0) / 1024).toFixed(1)} KB/s`}
          color="#4CAF50"
        />
      </View>

      {/* Protocol Breakdown */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Protocol Distribution</Text>
        <View style={styles.protocolList}>
          <ProtocolItem label="TCP" count={captureStats.tcp_packets || 0} />
          <ProtocolItem label="UDP" count={captureStats.udp_packets || 0} />
          <ProtocolItem label="ICMP" count={captureStats.icmp_packets || 0} />
          <ProtocolItem label="Other" count={captureStats.other_packets || 0} />
        </View>
      </View>

      {/* Network I/O */}
      {ioStats.bytes_sent && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Network I/O</Text>
          <View style={styles.ioStats}>
            <View style={styles.ioItem}>
              <Icon name="arrow-upward" size={24} color="#4CAF50" />
              <Text style={styles.ioLabel}>Sent</Text>
              <Text style={styles.ioValue}>
                {(ioStats.bytes_sent / 1024 / 1024).toFixed(2)} MB
              </Text>
            </View>
            <View style={styles.ioItem}>
              <Icon name="arrow-downward" size={24} color="#2196F3" />
              <Text style={styles.ioLabel}>Received</Text>
              <Text style={styles.ioValue}>
                {(ioStats.bytes_recv / 1024 / 1024).toFixed(2)} MB
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* Recent Threats */}
      {threatStats.by_type && Object.keys(threatStats.by_type).length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recent Threats</Text>
          {Object.entries(threatStats.by_type).map(([type, count]) => (
            <View key={type} style={styles.threatItem}>
              <Icon name="warning" size={20} color="#F44336" />
              <Text style={styles.threatType}>{type}</Text>
              <Text style={styles.threatCount}>{count}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

const StatCard = ({icon, title, value, color}) => (
  <View style={styles.statCard}>
    <Icon name={icon} size={32} color={color} />
    <Text style={styles.statValue}>{value}</Text>
    <Text style={styles.statLabel}>{title}</Text>
  </View>
);

const ProtocolItem = ({label, count}) => (
  <View style={styles.protocolItem}>
    <Text style={styles.protocolLabel}>{label}</Text>
    <Text style={styles.protocolCount}>{count}</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
  },
  loadingText: {
    marginTop: 10,
    color: '#ffffff',
    fontSize: 16,
  },
  card: {
    backgroundColor: '#2d2d2d',
    margin: 10,
    padding: 15,
    borderRadius: 10,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginLeft: 10,
  },
  button: {
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  startButton: {
    backgroundColor: '#4CAF50',
  },
  stopButton: {
    backgroundColor: '#F44336',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 5,
  },
  statCard: {
    backgroundColor: '#2d2d2d',
    width: '48%',
    margin: '1%',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 10,
  },
  statLabel: {
    fontSize: 12,
    color: '#b0b0b0',
    marginTop: 5,
  },
  protocolList: {
    marginTop: 10,
  },
  protocolItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#3d3d3d',
  },
  protocolLabel: {
    color: '#ffffff',
    fontSize: 14,
  },
  protocolCount: {
    color: '#2196F3',
    fontSize: 14,
    fontWeight: 'bold',
  },
  ioStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 15,
  },
  ioItem: {
    alignItems: 'center',
  },
  ioLabel: {
    color: '#b0b0b0',
    fontSize: 12,
    marginTop: 5,
  },
  ioValue: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 5,
  },
  threatItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#3d3d3d',
  },
  threatType: {
    flex: 1,
    color: '#ffffff',
    fontSize: 14,
    marginLeft: 10,
  },
  threatCount: {
    color: '#F44336',
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default DashboardScreen;
