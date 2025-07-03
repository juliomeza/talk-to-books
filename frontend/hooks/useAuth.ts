"use client";

import { useState, useEffect } from "react";
import { auth } from "@/lib/firebase";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  onAuthStateChanged,
  User
} from "firebase/auth";

export default function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Set up auth state listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    // Clean up subscription
    return () => unsubscribe();
  }, []);

  // Sign in with email and password
  const signInWithEmail = async (email: string, password: string) => {
    setError(null);
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      setUser(userCredential.user);
      return userCredential.user;
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  // Sign up with email and password
  const signUpWithEmail = async (email: string, password: string) => {
    setError(null);
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      setUser(userCredential.user);
      return userCredential.user;
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  // Sign in with Google
  const signInWithGoogle = async () => {
    setError(null);
    const provider = new GoogleAuthProvider();
    try {
      const userCredential = await signInWithPopup(auth, provider);
      setUser(userCredential.user);
      return userCredential.user;
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  // Sign out
  const logout = async () => {
    setError(null);
    try {
      await signOut(auth);
      setUser(null);
    } catch (error: any) {
      setError(error.message);
      throw error;
    }
  };

  // Get auth token
  const getToken = async () => {
    if (!user) return null;
    try {
      const token = await user.getIdToken();
      return token;
    } catch (error) {
      console.error("Error getting token:", error);
      return null;
    }
  };

  return {
    user,
    loading,
    error,
    signInWithEmail,
    signUpWithEmail,
    signInWithGoogle,
    logout,
    getToken
  };
}
