export type DocumentRole = "owner" | "editor" | "viewer";

export interface DocumentSummary {
  id: number;
  title: string;
  owner_id: number;
  created_at: string;
  updated_at?: string | null;
  role?: DocumentRole;
}

export interface DocumentDetail extends DocumentSummary {
  content?: string | null;
}

export interface CreateDocumentPayload {
  title: string;
}

export interface UpdateDocumentPayload {
  title?: string;
}

export interface ShareDocumentPayload {
  user_id: number;
  role: DocumentRole;
}