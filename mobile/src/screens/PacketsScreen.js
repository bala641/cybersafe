/**
 * Packets Screen - Real-time packet capture view
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {getPackets} from '../api/client';
import CONFIG from '../config';

const PacketsScreen = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [packets, setPackets] = useState([]);

  useEffect(() => {
    loadPackets();
    const interval = setInterval(loadPackets, CONFIG.refreshIntervals.packets);
    return () => clearInterval(interval);
  }, []);

  const loadPackets = async () => {
    try {
      const data = await getPackets(CONFIG.limits.packets);
      setPackets(data);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error('Error loading packets:', error);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getProtocolColor = (protocol) => {
    switch (protocol) {
      case 'TCP': return '#2196F3';
      case 'UDP': return '#FF9800';
      case 'ICMP': return '#9C27B0';
      case 'ARP': return '#4CAF50';
      default: return '#757575';
    }
  };

  const getProtocolIcon = (protocol) => {
    switch (protocol) {
      case 'TCP': return 'swap-horiz';
      case 'UDP': return 'wifi-tethering';
      case 'ICMP': return 'error-outline';
      default: return 'device-unknown';
    }
  };

  const renderPacket = ({item}) => {
    const time = new Date(item.timestamp).toLocaleTimeString();
    const protocol = item.protocol || 'UNKNOWN';
    
    return (
      <View style={styles.packetCard}>
        <View style={styles.packetHeader}>
          <Icon 
            name={getProtocolIcon(protocol)} 
            size={20} 
            color={getProtocolColor(protocol)} 
          />
          <Text style={[styles.protocol, {color: getProtocolColor(protocol)}]}>
            {protocol}
          </Text>
          <Text style={styles.time}>{time}</Text>
          <Text style={styles.number}>#{item.number}</Text>
        </View>
        
        <View style={styles.packetBody}>
          <View style={styles.addressRow}>
            <Icon name="arrow-forward" size={16} color="#b0b0b0" />
            <Text style={styles.addressLabel}>From:</Text>
            <Text style={styles.address}>{item.src_ip || 'N/A'}</Text>
            {item.src_port && (
              <Text style={styles.port}>:{item.src_port}</Text>
            )}
          </View>
          
          <View style={styles.addressRow}>
            <Icon name="arrow-forward" size={16} color="#b0b0b0" />
            <Text style={styles.addressLabel}>To:</Text>
            <Text style={styles.address}>{item.dst_ip || 'N/A'}</Text>
            {item.dst_port && (
              <Text style={styles.port}>:{item.dst_port}</Text>
            )}
          </View>
        </View>
        
        <View style={styles.packetFooter}>
          <Text style={styles.length}>{item.length} bytes</Text>
          <Text style={styles.summary} numberOfLines={1}>
            {item.summary}
          </Text>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerText}>
          {packets.length} packets
        </Text>
      </View>
      
      <FlatList
        data={packets}
        renderItem={renderPacket}
        keyExtractor={(item, index) => `${item.number}-${index}`}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={() => {
              setRefreshing(true);
              loadPackets();
            }} 
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="inbox" size={64} color="#757575" />
            <Text style={styles.emptyText}>No packets captured yet</Text>
            <Text style={styles.emptySubtext}>Start monitoring to see packets</Text>
          </View>
        }
      />
    </View>
  );
};

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
  header: {
    backgroundColor: '#2d2d2d',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#3d3d3d',
  },
  headerText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  packetCard: {
    backgroundColor: '#2d2d2d',
    margin: 10,
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#2196F3',
  },
  packetHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  protocol: {
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  time: {
    flex: 1,
    color: '#b0b0b0',
    fontSize: 12,
    marginLeft: 10,
  },
  number: {
    color: '#757575',
    fontSize: 12,
  },
  packetBody: {
    marginBottom: 10,
  },
  addressRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 3,
  },
  addressLabel: {
    color: '#b0b0b0',
    fontSize: 12,
    marginLeft: 5,
    width: 40,
  },
  address: {
    color: '#ffffff',
    fontSize: 12,
    fontFamily: 'monospace',
  },
  port: {
    color: '#2196F3',
    fontSize: 12,
    fontFamily: 'monospace',
  },
  packetFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#3d3d3d',
  },
  length: {
    color: '#FF9800',
    fontSize: 11,
  },
  summary: {
    flex: 1,
    color: '#757575',
    fontSize: 11,
    marginLeft: 10,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    color: '#ffffff',
    fontSize: 18,
    marginTop: 20,
  },
  emptySubtext: {
    color: '#757575',
    fontSize: 14,
    marginTop: 10,
  },
});

export default PacketsScreen;
