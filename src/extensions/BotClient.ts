import {AkairoClient, CommandHandler, InhibitorHandler, ListenerHandler} from 'discord-akairo'
import {ApiHelper} from "./ApiHelper";
import * as path from "path"

export interface BotConfig {
    token: string,
    owners: string | string[],
    prefix: string
}

export class BotClient extends AkairoClient {
    public apiHelper: ApiHelper
    public config: BotConfig
    public listenerHandler: ListenerHandler
    public inhibitorHandler: InhibitorHandler
    public commandHandler: CommandHandler
    constructor(config: BotConfig) {
        super({
            ownerID: config.owners
        }, {
            allowedMentions: {parse: ["users"]} // No everyone or role mentions by default
        })
        // Create ApiHelper
        this.apiHelper = new ApiHelper(config.token)

        // Set token
        this.token = config.token

        // Set config
        this.config = config

        // Create listener handler
        this.listenerHandler = new ListenerHandler(this, {
            directory: path.join(__dirname, '..', 'listeners'),
            automateCategories: true
        });

        // Create inhibitor handler
        this.inhibitorHandler = new InhibitorHandler(this, {
            directory: path.join(__dirname, '..', 'inhibitors'),
            automateCategories: true,
        });

        // Create command handler
        this.commandHandler = new CommandHandler(this, {
            directory: path.join(__dirname, '..', 'commands'),
            prefix: this.config.prefix,
            allowMention: true,
            handleEdits: true,
            commandUtil: true,
            commandUtilLifetime: 3e5,
            argumentDefaults: {
                prompt: {
                    timeout: 'Timed out.',
                    ended: 'Too many tries.',
                    cancel: 'Canceled.',
                    retries: 3,
                    time: 3e4,
                }
            },
            ignorePermissions: this.config.owners,
            ignoreCooldown: this.config.owners,
        });
    }

    // Initialize everything
    private async _init(): Promise<void> {
        this.commandHandler.useListenerHandler(this.listenerHandler);
        this.commandHandler.useInhibitorHandler(this.inhibitorHandler);
        this.listenerHandler.setEmitters({
            commandHandler: this.commandHandler,
            listenerHandler: this.listenerHandler,
            process
        });
        // loads all the handlers
        const loaders = {
            commands: this.commandHandler,
            listeners: this.listenerHandler,
            inhibitors: this.inhibitorHandler,
        };
        for (const loader of Object.keys(loaders)) {
            try {
                loaders[loader].loadAll();
                console.log('Successfully loaded ' + loader + '.');
            } catch (e) {
                console.error('Unable to load loader ' + loader + ' with error ' + e);
            }
        }
    }

    public async start(): Promise<string> {
        await this._init();
        return this.login(this.config.token);
    }

    public destroy(relogin = true): void {
        super.destroy();
        if (relogin) {
            this.login(this.config.token);
        }
    }
}