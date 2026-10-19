/**
 * Threats Screen - Display detected threats
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {getThreats} from '../api/client';
import CONFIG from '../config';

const ThreatsScreen = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [threats, setThreats] = useState([]);
  const [filter, setFilter] = useState(null);

  useEffect(() => {
    loadThreats();
    const interval = setInterval(loadThreats, CONFIG.refreshIntervals.threats);
    return () => clearInterval(interval);
  }, [filter]);

  const loadThreats = async () => {
    try {
      const data = await getThreats(CONFIG.limits.threats, filter);
      setThreats(data);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error('Error loading threats:', error);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return '#D32F2F';
      case 'HIGH': return '#F44336';
      case 'MEDIUM': return '#FF9800';
      case 'LOW': return '#FFC107';
      default: return '#757575';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'report';
      case 'HIGH': return 'warning';
      case 'MEDIUM': return 'error-outline';
      case 'LOW': return 'info-outline';
      default: return 'help-outline';
    }
  };

  const getThreatIcon = (type) => {
    if (type.includes('SCAN')) return 'search';
    if (type.includes('FLOOD') || type.includes('DDOS')) return 'waves';
    if (type.includes('EXFILTRATION')) return 'cloud-upload';
    if (type.includes('PORT')) return 'router';
    return 'security';
  };

  const renderThreat = ({item}) => {
    const time = new Date(item.timestamp).toLocaleTimeString();
    const severity = item.severity || 'UNKNOWN';
    const type = item.type || 'UNKNOWN';
    
    return (
      <View style={[styles.threatCard, {borderLeftColor: getSeverityColor(severity)}]}>
        <View style={styles.threatHeader}>
          <View style={styles.threatHeaderLeft}>
            <Icon 
              name={getSeverityIcon(severity)} 
              size={24} 
              color={getSeverityColor(severity)} 
            />
            <View style={styles.threatHeaderText}>
              <Text style={[styles.severity, {color: getSeverityColor(severity)}]}>
                {severity}
              </Text>
              <Text style={styles.time}>{time}</Text>
            </View>
          </View>
          <Icon 
            name={getThreatIcon(type)} 
            size={24} 
            color="#757575" 
          />
        </View>
        
        <Text style={styles.threatType}>{type.replace(/_/g, ' ')}</Text>
        <Text style={styles.description}>{item.description}</Text>
        
        {item.source_ip && (
          <View style={styles.detailRow}>
            <Icon name="location-on" size={16} color="#b0b0b0" />
            <Text style={styles.detailLabel}>Source:</Text>
            <Text style={styles.detailValue}>{item.source_ip}</Text>
          </View>
        )}
        
        {item.target_ip && (
          <View style={styles.detailRow}>
            <Icon name="gps-fixed" size={16} color="#b0b0b0" />
            <Text style={styles.detailLabel}>Target:</Text>
            <Text style={styles.detailValue}>{item.target_ip}</Text>
          </View>
        )}
        
        {item.port_count && (
          <View style={styles.detailRow}>
            <Icon name="apps" size={16} color="#b0b0b0" />
            <Text style={styles.detailLabel}>Ports:</Text>
            <Text style={styles.detailValue}>{item.port_count}</Text>
          </View>
        )}
      </View>
    );
  };

  const FilterButton = ({label, value}) => (
    <TouchableOpacity
      style={[
        styles.filterButton,
        filter === value && styles.filterButtonActive
      ]}
      onPress={() => setFilter(filter === value ? null : value)}>
      <Text style={[
        styles.filterButtonText,
        filter === value && styles.filterButtonTextActive
      ]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.filterBar}>
        <FilterButton label="All" value={null} />
        <FilterButton label="Critical" value="CRITICAL" />
        <FilterButton label="High" value="HIGH" />
        <FilterButton label="Medium" value="MEDIUM" />
      </View>
      
      <View style={styles.header}>
        <Icon name="security" size={20} color="#F44336" />
        <Text style={styles.headerText}>
          {threats.length} threat{threats.length !== 1 ? 's' : ''} detected
        </Text>
      </View>
      
      <FlatList
        data={threats}
        renderItem={renderThreat}
        keyExtractor={(item, index) => `threat-${index}`}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={() => {
              setRefreshing(true);
              loadThreats();
            }} 
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="verified-user" size={64} color="#4CAF50" />
            <Text style={styles.emptyText}>No threats detected</Text>
            <Text style={styles.emptySubtext}>Your network is secure</Text>
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
  filterBar: {
    flexDirection: 'row',
    backgroundColor: '#2d2d2d',
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#3d3d3d',
  },
  filterButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    marginRight: 8,
    borderRadius: 20,
    backgroundColor: '#3d3d3d',
  },
  filterButtonActive: {
    backgroundColor: '#2196F3',
  },
  filterButtonText: {
    color: '#b0b0b0',
    fontSize: 12,
  },
  filterButtonTextActive: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2d2d2d',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#3d3d3d',
  },
  headerText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  threatCard: {
    backgroundColor: '#2d2d2d',
    margin: 10,
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
  },
  threatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  threatHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  threatHeaderText: {
    marginLeft: 10,
  },
  severity: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  time: {
    color: '#757575',
    fontSize: 11,
    marginTop: 2,
  },
  threatType: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  description: {
    color: '#b0b0b0',
    fontSize: 14,
    marginBottom: 12,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 3,
  },
  detailLabel: {
    color: '#757575',
    fontSize: 12,
    marginLeft: 5,
    width: 60,
  },
  detailValue: {
    color: '#ffffff',
    fontSize: 12,
    fontFamily: 'monospace',
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

export default ThreatsScreen;
