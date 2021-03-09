import { BotListener } from '../../lib/extensions/BotListener';

export default class CommandBlockedListener extends BotListener {
	public constructor() {
		super('ready', {
			emitter: 'client',
			event: 'ready'
		});
	}

	public async exec(): Promise<void> {
		console.log('Bot ready, running db post init...');
		await this.client.dbPostInit();
		console.log(`Sucessfully logged in as ${this.client.user.tag}`);
	}
}
