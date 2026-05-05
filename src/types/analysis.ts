export interface AnalysisResult {
  score: number;
  label: 'clean' | 'warning' | 'suspicious' | 'info' | 'error';
  details: Record<string, unknown>;
  image: string | null;
}

export interface FullAnalysis {
  exif: AnalysisResult;
  ela: AnalysisResult;
  fft: AnalysisResult;
  pixel_stats: AnalysisResult;
  clone_detection: AnalysisResult;
  face_detection: AnalysisResult;
  ai_features: AnalysisResult;
  ai_score: number;
  ai_label: 'clean' | 'warning' | 'suspicious';
  manipulation_score: number;
  manipulation_label: 'clean' | 'warning' | 'suspicious';
}

export interface ComparisonAnalysis {
  diff: AnalysisResult;
  similarity: AnalysisResult;
}
