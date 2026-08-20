export interface UserSummary {
  id: string;
  email: string;
  name: string;
  status: string;
}

export interface OrganizationSummary {
  id: string;
  name: string;
  slug: string;
}

export interface MembershipSummary {
  organization_id: string;
  organization_name: string;
  role: "owner" | "admin" | "editor" | "viewer";
}

export interface AuthResponse {
  token: string | null;
  user: UserSummary;
  active_organization_id: string | null;
  memberships: MembershipSummary[];
}

export interface RegisterResponse {
  token: string;
  user: UserSummary;
  organization: OrganizationSummary;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}
