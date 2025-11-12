// -----------------------------------------------------------------------------
// File: QualityBadge.jsx
// Description: Quality badge component for ReqEngine - displays use case quality
//              scores with color-coded indicators and formatted labels.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import React from 'react';
import { getQualityColor, getQualityLabel } from '../utils/formatters';

function QualityBadge({ score }) {
  const colorClass = getQualityColor(score);
  const label = getQualityLabel(score);

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${colorClass}`}>
      {label} ({score}/100)
    </span>
  );
}

export default QualityBadge;