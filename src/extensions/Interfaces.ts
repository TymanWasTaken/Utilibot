export interface Application {
    id: string;
    name: string;
    icon?: null;
    description: string;
    summary: string;
    hook: boolean;
    bot_public: boolean;
    bot_require_code_grant: boolean;
    verify_key: string;
    owner: Owner;
    team: Team;
}
export interface Owner {
    id: string;
    username: string;
    avatar?: null;
    discriminator: string;
    public_flags: number;
    flags: number;
}
export interface Team {
    id: string;
    icon: string;
    name: string;
    owner_user_id: string;
    members?: (TeamMember)[] | null;
}
export interface TeamMember {
    user: User;
    team_id: string;
    membership_state: number;
    permissions?: (string)[] | null;
}
export interface User {
    id: string;
    username: string;
    avatar: string;
    discriminator: string;
    public_flags: number;
}
