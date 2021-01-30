import {ClientUtil} from 'discord-akairo'
import {BotClient} from './BotClient'
import {User} from 'discord.js'
import {promisify} from 'util'
import {exec} from 'child_process'
import got from 'got'

interface hastebinRes {
	key: string
}

export class Util extends ClientUtil {
	public client: BotClient
	public hasteURLs = [
		'https://hst.sh',
		'https://hasteb.in',
		'https://hastebin.com',
		'https://mystb.in',
		'https://haste.clicksminuteper.net',
		'https://paste.pythondiscord.com',
		'https://haste.unbelievaboat.com',
		'https://haste.tyman.tech'
	]
	private exec = promisify(exec)
	constructor(client: BotClient) {
		super(client)
	}

	public async mapIDs(ids: string[]): Promise<User[]>
	public async mapIDs(ids: string[], tags: true): Promise<`${string}#${number}`[]>
	public async mapIDs(ids: string[], tags: false): Promise<User[]>
	public async mapIDs(ids: string[], tags?: boolean): Promise<User[] | string[]> {
		if (tags) {
			return (await Promise.all(
				ids.map(id => this.client.users.fetch(id))
			)).map(user => user.tag)
		} else {
			return await Promise.all(
				ids.map(id => this.client.users.fetch(id))
			)
		}
	}

	public capitalize(text: string): string {
		return text.charAt(0).toUpperCase() + text.slice(1)
	}

	public async shell(command: string): Promise<{
		stdout: string,
		stderr: string
	}> {
		return await this.exec(command)
	}

	public async haste(content: string): Promise<string> {
		for (const url of this.hasteURLs) {
			try {
				const res: hastebinRes = await got.post(`${url}/documents`, { body: content }).json()
				return `${url}/${res.key}`
			} catch (e) {
				// pass
			}
		}
		throw new Error('No urls worked. (wtf)')
	}
}