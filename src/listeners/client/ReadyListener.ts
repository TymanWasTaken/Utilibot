import { BotListener } from '../../extensions/BotListener';

export default class CommandBlockedListener extends BotListener {
	public constructor() {
		super('ready', {
			emitter: 'client',
			event: 'ready'
		});
	}

	public async exec(): Promise<void> {
		console.log(`Sucessfully logged in as ${this.client.user.tag}`);
	}
}
