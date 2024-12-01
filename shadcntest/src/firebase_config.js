// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCm1IlfQFgT5UKw9udEtBiJQ_z7Arta-Q8",
  authDomain: "sample-firebase-ai-app-91084.firebaseapp.com",
  projectId: "sample-firebase-ai-app-91084",
  storageBucket: "sample-firebase-ai-app-91084.firebasestorage.app",
  messagingSenderId: "950643987000",
  appId: "1:950643987000:web:d8500457ad3b8d7dabcccd",
};
//s
// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

export { auth, provider, db };
