/**
 * Ports Screen - Display active ports and connections
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {getPorts} from '../api/client';

const PortsScreen = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [portsData, setPortsData] = useState({listening: [], connections: []});
  const [showConnections, setShowConnections] = useState(false);

  useEffect(() => {
    loadPorts();
  }, []);

  const loadPorts = async () => {
    try {
      const data = await getPorts();
      setPortsData(data);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error('Error loading ports:', error);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getPortColor = (port) => {
    // Suspicious ports
    const suspiciousPorts = [23, 135, 139, 445, 1433, 3306, 3389, 5432];
    if (suspiciousPorts.includes(port)) return '#F44336';
    
    // Common ports
    if (port === 80 || port === 443) return '#4CAF50';
    if (port < 1024) return '#FF9800';
    
    return '#2196F3';
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl 
          refreshing={refreshing} 
          onRefresh={() => {
            setRefreshing(true);
            loadPorts();
          }} 
        />
      }>
      
      {/* Toggle Buttons */}
      <View style={styles.toggleContainer}>
        <TouchableOpacity
          style={[styles.toggleButton, !showConnections && styles.toggleButtonActive]}
          onPress={() => setShowConnections(false)}>
          <Icon 
            name="router" 
            size={20} 
            color={!showConnections ? '#ffffff' : '#b0b0b0'} 
          />
          <Text style={[
            styles.toggleText,
            !showConnections && styles.toggleTextActive
          ]}>
            Listening Ports
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.toggleButton, showConnections && styles.toggleButtonActive]}
          onPress={() => setShowConnections(true)}>
          <Icon 
            name="swap-horiz" 
            size={20} 
            color={showConnections ? '#ffffff' : '#b0b0b0'} 
          />
          <Text style={[
            styles.toggleText,
            showConnections && styles.toggleTextActive
          ]}>
            Connections
          </Text>
        </TouchableOpacity>
      </View>

      {!showConnections ? (
        // Listening Ports
        <View>
          <View style={styles.header}>
            <Icon name="router" size={20} color="#2196F3" />
            <Text style={styles.headerText}>
              {portsData.listening.length} listening port{portsData.listening.length !== 1 ? 's' : ''}
            </Text>
          </View>
          
          {portsData.listening.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Icon name="inbox" size={64} color="#757575" />
              <Text style={styles.emptyText}>No listening ports</Text>
            </View>
          ) : (
            portsData.listening.map((port, index) => (
              <View key={index} style={styles.portCard}>
                <View style={styles.portHeader}>
                  <View style={[
                    styles.portBadge,
                    {backgroundColor: getPortColor(port.port)}
                  ]}>
                    <Text style={styles.portNumber}>{port.port}</Text>
                  </View>
                  <View style={styles.portInfo}>
                    <Text style={styles.processName}>
                      {port.process || 'Unknown'}
                    </Text>
                    <Text style={styles.portDetails}>
                      PID: {port.pid || 'N/A'}
                    </Text>
                  </View>
                </View>
                
                {port.ip && (
                  <View style={styles.detailRow}>
                    <Icon name="location-on" size={16} color="#b0b0b0" />
                    <Text style={styles.detailLabel}>Bind Address:</Text>
                    <Text style={styles.detailValue}>{port.ip}</Text>
                  </View>
                )}
              </View>
            ))
          )}
        </View>
      ) : (
        // Active Connections
        <View>
          <View style={styles.header}>
            <Icon name="swap-horiz" size={20} color="#FF9800" />
            <Text style={styles.headerText}>
              {portsData.connections.length} active connection{portsData.connections.length !== 1 ? 's' : ''}
            </Text>
          </View>
          
          {portsData.connections.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Icon name="cloud-off" size={64} color="#757575" />
              <Text style={styles.emptyText}>No active connections</Text>
            </View>
          ) : (
            portsData.connections.map((conn, index) => (
              <View key={index} style={styles.connectionCard}>
                <View style={styles.connectionHeader}>
                  <Icon 
                    name={conn.status === 'ESTABLISHED' ? 'check-circle' : 'pending'} 
                    size={20} 
                    color={conn.status === 'ESTABLISHED' ? '#4CAF50' : '#FF9800'} 
                  />
                  <Text style={styles.connectionStatus}>{conn.status}</Text>
                  {conn.process && (
                    <Text style={styles.connectionProcess}>{conn.process}</Text>
                  )}
                </View>
                
                <View style={styles.connectionFlow}>
                  <View style={styles.endpoint}>
                    <Text style={styles.endpointLabel}>Local</Text>
                    <Text style={styles.endpointValue}>
                      :{conn.local_port}
                    </Text>
                  </View>
                  
                  <Icon name="arrow-forward" size={24} color="#2196F3" />
                  
                  <View style={styles.endpoint}>
                    <Text style={styles.endpointLabel}>Remote</Text>
                    <Text style={styles.endpointValue}>
                      {conn.remote_ip}:{conn.remote_port}
                    </Text>
                  </View>
                </View>
              </View>
            ))
          )}
        </View>
      )}
    </ScrollView>
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
  toggleContainer: {
    flexDirection: 'row',
    backgroundColor: '#2d2d2d',
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#3d3d3d',
  },
  toggleButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 12,
    marginHorizontal: 5,
    borderRadius: 8,
    backgroundColor: '#3d3d3d',
  },
  toggleButtonActive: {
    backgroundColor: '#2196F3',
  },
  toggleText: {
    color: '#b0b0b0',
    fontSize: 14,
    marginLeft: 8,
  },
  toggleTextActive: {
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
  portCard: {
    backgroundColor: '#2d2d2d',
    margin: 10,
    padding: 15,
    borderRadius: 8,
  },
  portHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  portBadge: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  portNumber: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  portInfo: {
    flex: 1,
    marginLeft: 15,
  },
  processName: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  portDetails: {
    color: '#b0b0b0',
    fontSize: 12,
    marginTop: 4,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  detailLabel: {
    color: '#757575',
    fontSize: 12,
    marginLeft: 5,
    marginRight: 8,
  },
  detailValue: {
    color: '#ffffff',
    fontSize: 12,
    fontFamily: 'monospace',
  },
  connectionCard: {
    backgroundColor: '#2d2d2d',
    margin: 10,
    padding: 15,
    borderRadius: 8,
  },
  connectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  connectionStatus: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  connectionProcess: {
    flex: 1,
    color: '#b0b0b0',
    fontSize: 12,
    marginLeft: 10,
    textAlign: 'right',
  },
  connectionFlow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  endpoint: {
    flex: 1,
  },
  endpointLabel: {
    color: '#757575',
    fontSize: 11,
    marginBottom: 4,
  },
  endpointValue: {
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
});

export default PortsScreen;
