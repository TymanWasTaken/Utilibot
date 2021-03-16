import { ClientUtil } from 'discord-akairo';
import { BotClient } from './BotClient';
import { User } from 'discord.js';
import { promisify } from 'util';
import { exec } from 'child_process';
import got from 'got';

interface hastebinRes {
	key: string;
}

export class Util extends ClientUtil {
	public client: BotClient;
	public hasteURLs = [
		'https://hst.sh',
		'https://hasteb.in',
		'https://hastebin.com',
		'https://mystb.in',
		'https://haste.clicksminuteper.net',
		'https://paste.pythondiscord.com',
		'https://haste.unbelievaboat.com',
		'https://haste.tyman.tech'
	];
	private exec = promisify(exec);
	constructor(client: BotClient) {
		super(client);
	}

	public async mapIDs(ids: string[]): Promise<User[]> {
		return await Promise.all(ids.map((id) => this.client.users.fetch(id)));
	}

	public capitalize(text: string): string {
		return text.charAt(0).toUpperCase() + text.slice(1);
	}

	public async shell(
		command: string
	): Promise<{
		stdout: string;
		stderr: string;
	}> {
		return await this.exec(command);
	}

	public async haste(content: string): Promise<string> {
		for (const url of this.hasteURLs) {
			try {
				const res: hastebinRes = await got
					.post(`${url}/documents`, { body: content })
					.json();
				return `${url}/${res.key}`;
			} catch (e) {
				// pass
			}
		}
		throw new Error('No urls worked. (wtf)');
	}

	public devLog(content: unknown): void {
		if (this.client.config.dev) console.log(content);
	}

	public async resolveUserAsync(text: string): Promise<User | null> {
		const idReg = /\d{17,19}/;
		const idMatch = text.match(idReg);
		if (idMatch) {
			try {
				const user = await this.client.users.fetch(text);
				return user;
			} catch {
				// pass
			}
		}
		const mentionReg = /<@!?(?<id>\d{17,19})>/;
		const mentionMatch = text.match(mentionReg);
		if (mentionMatch) {
			try {
				const user = await this.client.users.fetch(mentionMatch.groups.id);
				return user;
			} catch {
				// pass
			}
		}
		const user = this.client.users.cache.find((u) => u.username === text);
		if (user) return user;
		return null;
	}

	public ordinal(n: number): string {
		const s = ['th', 'st', 'nd', 'rd'],
			v = n % 100;
		return n + (s[(v - 20) % 10] || s[v] || s[0]);
	}
}
