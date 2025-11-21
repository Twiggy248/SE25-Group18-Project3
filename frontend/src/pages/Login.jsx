import React from "react";
import { ThemeControls } from "../context/ThemeContext";

export default function Login() {
  return (
    <div className="h-screen w-full flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors relative">
      
      <div className="bg-white dark:bg-gray-800 p-10 rounded-xl shadow-md text-center border border-gray-200 dark:border-gray-700">
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">
          Sign in to ReqEngine
        </h1>

        <a
          href="http://localhost:8000/auth/google"
          className="inline-block px-6 py-3 bg-indigo-600 dark:bg-indigo-500 text-white rounded-lg hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors"
        >
          Sign in with Google
        </a>
      </div>
    </div>
  );
}