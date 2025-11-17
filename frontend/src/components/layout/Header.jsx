// -----------------------------------------------------------------------------
// File: Header.jsx
// Description: Header layout component for ReqEngine - displays logo, navigation,
//              and main application branding across all pages.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React from 'react';
import { Link } from 'react-router-dom';
import logoImage from "../../assets/logoo.png";

function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-2">
      <div className="flex items-center">
        {/* Logo - Just RE part */}
        <Link to="/" className="flex items-center">
          <div className="w-9 h-9 overflow-hidden">
            <img 
              src={logoImage} 
              alt="ReqEngine" 
              className="h-full object-cover object-left"
              style={{ width: '140%' }}
            />
          </div>
        </Link>
      </div>
    </header>
  );
}

export default Header;