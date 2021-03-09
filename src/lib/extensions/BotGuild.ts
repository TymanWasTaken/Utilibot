import { Guild, Structures } from 'discord.js';
import { BotClient } from './BotClient';
import { Guild as GuildModel } from '../types/Models';

export class GuildSettings {
	private guild: BotGuild;
	constructor(guild: BotGuild) {
		this.guild = guild;
	}
	public async getPrefix(): Promise<string> {
		return await GuildModel.findByPk(this.guild.id).then(
			(gm) => gm.prefix as string
		);
	}
	public async setPrefix(value: string): Promise<void> {
		const entry = await GuildModel.findByPk(this.guild.id);
		entry.prefix = value;
		await entry.save();
	}
}

export class BotGuild extends Guild {
	constructor(client: BotClient, data: Record<string, unknown>) {
		super(client, data);
	}
	static install(): void {
		Structures.extend('Guild', () => BotGuild);
	}
	public settings = new GuildSettings(this);
}
