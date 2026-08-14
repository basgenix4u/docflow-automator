export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface Portal {
  id: string;
  name: string;
  base_url: string;
  auth_type: string;
  username_field: string;
  password_field: string;
  demo_username?: string;
  demo_password?: string;
  status: string;
}

export interface WorkflowStep {
  action: string;
  selector?: string;
  value?: string;
  target_var?: string;
}

export interface Workflow {
  id: string;
  portal_id: string;
  name: string;
  description?: string;
  steps_json: string;
  target_format: string;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export interface WorkflowRun {
  id: string;
  workflow_id: string;
  status: string;
  execution_logs: string;
  extracted_data_json: string;
  duration_ms: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface Document {
  id: string;
  workflow_run_id?: string;
  title: string;
  page_format: string;
  page_count: number;
  file_size_bytes: number;
  created_at: string;
}

export interface Vulnerability {
  severity: string;
  title: string;
  description: string;
}

export interface SecurityTest {
  name: string;
  category: string;
  passed: boolean;
  details: string;
  value?: string;
}

export interface SecurityScan {
  id: string;
  portal_id: string;
  status: string;
  score: number;
  vulnerabilities_found: number;
  tests_executed_json: string;
  report_json: string;
  created_at: string;
}

export interface HealthCheckResponse {
  status: string;
  system: string;
  timestamp: string;
  target_portal: string;
  database_online?: boolean;
  storage_dir?: string;
  storage_ready: boolean;
  auth_required_for_operators?: boolean;
}
