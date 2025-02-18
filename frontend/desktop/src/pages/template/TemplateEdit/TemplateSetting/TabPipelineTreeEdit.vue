/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <bk-sideslider
        :is-show="true"
        :width="800"
        :title="$t('模板数据')"
        :quick-close="true"
        :before-close="closeTab">
        <div class="pipeline-tree-wrap" slot="content">
            <div class="code-wrapper">
                <full-code-editor
                    :value="template"
                    :options="{ readOnly: (isViewMode || !hasAdminPerm), language: 'json' }"
                    @input="onDataChange">
                </full-code-editor>
            </div>
            <div class="btn-wrap">
                <template v-if="hasAdminPerm">
                    <bk-button v-if="!isViewMode" class="save-btn" theme="primary" @click="onConfirm">{{ $t('保存') }}</bk-button>
                    <bk-button theme="default" @click="closeTab">{{ isViewMode ? $t('关闭') : $t('取消') }}</bk-button>
                </template>
                <bk-button v-else theme="primary" @click="closeTab">{{ $t('关闭') }}</bk-button>
            </div>
        </div>
    </bk-sideslider>
</template>

<script>
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'
    import { mapState, mapGetters } from 'vuex'
    import validatePipeline from '@/utils/validatePipeline.js'
    export default {
        name: 'TabPipelineTreeEdit',
        components: {
            FullCodeEditor
        },
        props: ['isShow', 'isViewMode'],
        data () {
            return {
                template: this.transPipelineTreeStr(),
                errorMessage: '',
                isDataChange: false
            }
        },
        computed: {
            ...mapState({
                hasAdminPerm: state => state.hasAdminPerm,
                infoBasicConfig: state => state.infoBasicConfig
            })
        },
        methods: {
            ...mapGetters('template/', [
                'getLocalTemplateData'
            ]),
            transPipelineTreeStr () {
                const templateData = this.getLocalTemplateData()
                return JSON.stringify(templateData, null, 4)
            },
            onDataChange (value) {
                if (value !== this.template) {
                    this.template = value
                    this.isDataChange = true
                }
            },
            onConfirm () {
                let pipelineData = {}
                try {
                    pipelineData = JSON.parse(this.template)
                } catch (error) {
                    this.$bkMessage({
                        theme: 'error',
                        ellipsisLine: 0,
                        message: error
                    })
                    return
                }
                const validateResult = validatePipeline.isPipelineDataValid(pipelineData)
                if (!validateResult.result) {
                    this.$bkMessage({
                        theme: 'error',
                        ellipsisLine: 0,
                        message: validateResult.message
                    })
                    return
                }
                this.$emit('modifyTemplateData', pipelineData)
                this.closeTab()
            },
            closeTab () {
                if (this.isDataChange) {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        cancelFn: () => {
                            this.$emit('closeTab')
                        }
                    })
                } else {
                    this.$emit('closeTab')
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';
    .pipeline-tree-wrap {
        height: calc(100vh - 60px);
    }
    .code-wrapper {
        position: relative;
        padding: 20px;
        height: calc(100% - 49px);
    }
    .btn-wrap {
        padding: 8px 20px;
        border-top: 1px solid #cacedb;
    }
</style>
