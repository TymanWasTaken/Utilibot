import {Application, Team} from "./Interfaces";
import got from 'got';

export class ApiHelper {
    public token: string

    /**
     * Creates the ApiHelper with the given object
     * @param token - The token used for api requests
     */
    constructor(token: string) {
        this.token = token
    }

    /**
     * Gets the team data from the discord api
     * @return Team - The Team fetched from the api
     */
    public async getTeam(): Promise<Team> {
        const API_ENDPOINT = "https://discord.com/api/v8/oauth2/applictions/@me"
        const apiResponse: Application = await got.get(API_ENDPOINT, {
            headers: {
                "Authorization": `Bot ${this.token}`,
                "User-Agent": "DiscordBot Utilibot v2 api helper"
            }
        }).json()
        return apiResponse.team
    }

    /**
     * Gets the list of ids for the current application team
     * @return Team Member IDs - The ids of the members of the current team
     */
    public async getTeamMemberIds(): Promise<string[]> {
        const team = await this.getTeam()
        return team.members.map(m => m.user.id)
    }
}