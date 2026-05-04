import React, { useCallback, useState } from 'react';

interface Props {
  onFileSelect: (files: File[]) => void;
  mode: 'single' | 'compare';
  disabled?: boolean;
}

export default function UploadZone({ onFileSelect, mode, disabled }: Props) {
  const [dragging, setDragging] = useState(false);

  const handleFiles = useCallback(
    (raw: File[]) => {
      const images = raw.filter((f) => f.type.startsWith('image/'));
      if (images.length === 0) return;
      onFileSelect(mode === 'compare' ? images.slice(0, 2) : [images[0]]);
    },
    [onFileSelect, mode]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      if (!disabled) handleFiles(Array.from(e.dataTransfer.files));
    },
    [disabled, handleFiles]
  );

  return (
    <div
      className={`upload-zone${dragging ? ' upload-zone--dragging' : ''}${disabled ? ' upload-zone--disabled' : ''}`}
      onDrop={handleDrop}
      onDragOver={(e) => { e.preventDefault(); if (!disabled) setDragging(true); }}
      onDragLeave={() => setDragging(false)}
    >
      <input
        id="file-upload"
        type="file"
        accept="image/*"
        multiple={mode === 'compare'}
        className="upload-zone__input"
        disabled={disabled}
        onChange={(e) => {
          if (!disabled) handleFiles(Array.from(e.target.files || []));
          e.target.value = '';
        }}
      />
      <label htmlFor="file-upload" className="upload-zone__label">
        <span className="upload-zone__icon">↑</span>
        <p>ドラッグ＆ドロップ または クリックしてアップロード</p>
        <p className="upload-zone__sub">
          {mode === 'compare'
            ? '2枚まで選択（比較モード） — JPEG / PNG / WebP'
            : 'JPEG・PNG・WebP 対応 — 最大 20MB'}
        </p>
      </label>
    </div>
  );
}
