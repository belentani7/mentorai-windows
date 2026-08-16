// Este es un componente de ejemplo en React Native
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';

const AssistantApp = () => {
  const [response, setResponse] = useState(null);
  const [isActive, setIsActive] = useState(false);

  const handleCapture = () => {
    setIsActive(true);
    // En producción, aquí se llamaría al Core de Python a través de un puente nativo
    setTimeout(() => {
      setResponse({
        explanation: "El comando 'cd' se usa para cambiar de carpeta.",
        steps: ["1. Escribe cd", "2. Espacio", "3. Nombre carpeta"],
        security_tips: ["No entres en carpetas del sistema."]
      });
      setIsActive(false);
    }, 1000);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Asistente Educativo IA</Text>
      
      <TouchableOpacity 
        style={[styles.button, isActive && styles.buttonActive]} 
        onPress={handleCapture}
      >
        <Text style={styles.buttonText}>
          {isActive ? "Escaneando..." : "Analizar Pantalla"}
        </Text>
      </TouchableOpacity>

      {response && (
        <ScrollView style={styles.responseContainer}>
          <Text style={styles.subtitle}>Explicación:</Text>
          <Text style={styles.text}>{response.explanation}</Text>
          
          <Text style={styles.subtitle}>Pasos:</Text>
          {response.steps.map((step, index) => (
            <Text key={index} style={styles.text}>• {step}</Text>
          ))}

          <View style={styles.securityBox}>
            <Text style={styles.securityTitle}>🔒 Seguridad:</Text>
            {response.security_tips.map((tip, index) => (
              <Text key={index} style={styles.securityText}>- {tip}</Text>
            ))}
          </View>
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f5f5f5' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 20, color: '#333' },
  button: { backgroundColor: '#007AFF', padding: 15, borderRadius: 10, alignItems: 'center' },
  buttonActive: { backgroundColor: '#FF9500' },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: '600' },
  responseContainer: { marginTop: 20 },
  subtitle: { fontSize: 18, fontWeight: 'bold', marginTop: 15, color: '#444' },
  text: { fontSize: 16, color: '#666', marginTop: 5 },
  securityBox: { marginTop: 20, padding: 15, backgroundColor: '#E1F5FE', borderRadius: 10, borderLeftWidth: 5, borderLeftColor: '#0288D1' },
  securityTitle: { fontSize: 16, fontWeight: 'bold', color: '#01579B' },
  securityText: { fontSize: 14, color: '#0277BD', marginTop: 5 }
});

export default AssistantApp;
