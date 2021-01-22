import {BotClient} from './extensions/BotClient'
import config from "./config";

const client: BotClient = new BotClient(config);
client.start();