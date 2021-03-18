import {
	TextChannel,
	NewsChannel,
	DMChannel,
	Message,
	Structures
} from 'discord.js';
import { BotClient } from './BotClient';
import { Guild as GuildModel } from '../types/Models';
import { BotGuild } from './BotGuild';

export class GuildSettings {
	private message: BotMessage;
	constructor(message: BotMessage) {
		this.message = message;
	}
	public async getPrefix(): Promise<string> {
		return await GuildModel.findByPk(this.message.guild.id).then(
			(gm) => gm?.prefix || this.message.client.config.prefix
		);
	}
	public async setPrefix(value: string): Promise<void> {
		const entry = await GuildModel.findByPk(this.message.guild.id);
		entry.prefix = value;
		await entry.save();
	}
}

export class BotMessage extends Message {
	constructor(
		client: BotClient,
		data: Record<string, unknown>,
		channel: TextChannel | DMChannel | NewsChannel
	) {
		super(client, data, channel);
	}
	public guild: BotGuild;
	public client: BotClient;
	static install(): void {
		Structures.extend('Message', () => BotMessage);
	}
	public settings = new GuildSettings(this);
}
