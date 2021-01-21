import { AkairoClient } from 'discord-akairo'

class BotClient extends AkairoClient {
    public apiHelper
    constructor() {
        super({

        }, {
            allowedMentions: {parse: ["users"]} // No everyone or role mentions by default
        })
    }
}

export default BotClient