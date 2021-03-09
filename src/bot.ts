import { BotClient } from './extensions/BotClient';
import * as config from './config/options';

const client: BotClient = new BotClient(config);
client.start();
