// 示例 Scratch 扩展
class SampleExtension {
    constructor(runtime) {
        this.runtime = runtime;
    }

    getInfo() {
        return {
            id: 'sampleextension',
            name: '示例扩展',
            blocks: [
                {
                    opcode: 'sayHello',
                    blockType: 'command',
                    text: '说你好 [NAME]',
                    arguments: {
                        NAME: {
                            type: 'string',
                            defaultValue: '世界'
                        }
                    }
                },
                {
                    opcode: 'getDouble',
                    blockType: 'reporter',
                    text: '[NUM] 的两倍',
                    arguments: {
                        NUM: {
                            type: 'number',
                            defaultValue: 10
                        }
                    }
                }
            ]
        };
    }

    sayHello(args) {
        console.log(`你好, ${args.NAME}!`);
    }

    getDouble(args) {
        return args.NUM * 2;
    }
}

module.exports = SampleExtension;
