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
    <div
        :class="[
            'gateway-node',
            'branch-gateway',
            { 'fail-skip': node.status === 'FINISHED' && node.skip },
            { 'ready': node.ready },
            node.status ? node.status.toLowerCase() : ''
        ]">
        <div class="node-type-icon common-icon-node-branchgateway"></div>
        <div class="state-icon" v-if="isOpenTooltip">
            <span @click.stop="onGatewaySelectionClick">
                <i class="common-icon-skip"></i>
                {{ $t('跳过') }}
            </span>
        </div>
    </div>
</template>
<script>

    export default {
        name: 'BranchGateway',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        computed: {
            isOpenTooltip () {
                return this.node.status === 'FAILED'
            }
        },
        methods: {
            onGatewaySelectionClick () {
                this.$emit('onGatewaySelectionClick', this.node.id)
            }
        }
    }
</script>
