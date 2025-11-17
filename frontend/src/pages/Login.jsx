import React from "react";

export default function Login() {
  return (
    <div className="h-screen w-full flex items-center justify-center bg-gray-50">
      <div className="bg-white p-10 rounded-xl shadow-md text-center">
        <h1 className="text-3xl font-bold mb-6">Sign in to ReqEngine</h1>

        <a
          href="http://localhost:8000/auth/google"
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Sign in with Google
        </a>
      </div>
    </div>
  );
}