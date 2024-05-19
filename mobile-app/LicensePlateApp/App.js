import React, { useEffect, useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  FlatList,
  SafeAreaView,
  RefreshControl,
} from "react-native";
import axios from "axios";
import { Appbar, Card, Title, Paragraph } from "react-native-paper";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";
import { SafeAreaProvider } from "react-native-safe-area-context";

export default function App() {
  const [data, setData] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = () => {
    axios
      .get("http://192.168.56.1:5000/license-plates")
      .then((response) => {
        setData(response.data);
        setRefreshing(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setRefreshing(false);
      });
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const renderItem = ({ item }) => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.cardHeader}>
          <Icon name="car" size={24} color="#6200ee" />
          <Title style={styles.title}>{item.license_plate}</Title>
        </View>
        <Paragraph>{new Date(item.timestamp).toLocaleString()}</Paragraph>
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <Appbar.Header>
          <Appbar.Content title="License Plates" />
        </Appbar.Header>
        <FlatList
          data={data}
          renderItem={renderItem}
          keyExtractor={(item) => item._id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  list: {
    padding: 16,
  },
  card: {
    marginVertical: 8,
    borderRadius: 8,
    elevation: 4,
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  title: {
    marginLeft: 8,
    fontSize: 18,
    color: "#6200ee",
  },
});
