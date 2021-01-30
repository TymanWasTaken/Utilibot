import {BotInhibitor} from '../../extensions/BotInhibitor'
import {BotCommand} from '../../extensions/BotCommand'
import {Message} from 'discord.js'

export default class BlacklistInhibitor extends BotInhibitor {
	constructor() {
		super('blacklist', {
			reason: 'blacklist'
		})
	}

	public exec(message: Message, command?: BotCommand): boolean | Promise<boolean> {
		// This is just a placeholder for now
		return false
	}
}