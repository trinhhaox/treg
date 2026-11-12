<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>

          <!-- Two programs, one page, forked at the header: the credit referral program every user
               gets, and the invite-only cash tier behind it. A fork rather than a card under the
               referral column, because a card there read as step four of the referral program. The
               cash tier is hand-approved on purpose — hand-approval IS the anti-gaming design
               (money.md §Referrals) — so it is a form, not a self-serve toggle, and it shows to
               everyone, team or not, so a partner without a team yet can still apply. -->
          <h1>{{refTab==='partner' ? 'Đối tác liên kết (Affiliate)' : 'Giới thiệu bạn bè'}}</h1>
          <p class="sub" v-if="refTab==='partner'">Chia sẻ doanh thu, thanh toán bằng tiền mặt. Theo lời mời đặc biệt.</p>
          <p class="sub" v-else :style="ref.loaded ? null : {visibility:'hidden'}">Bạn bè nhận {{money(ref.terms.referred_micro)}} khi nạp từ
            {{money(ref.terms.min_topup_micro)}}. Bạn nhận {{money(ref.terms.referrer_micro)}},
            sau {{ref.terms.hold_days}} ngày.</p>
          <div class="tabs" style="max-width:720px">
            <button :class="{active:refTab==='friend'}" @click="refTab='friend'">Giới thiệu bạn bè</button>
            <button :class="{active:refTab==='partner'}" @click="refTab='partner'">Đối tác liên kết</button>
          </div>
          <div v-if="refTab==='partner'" style="max-width:720px">
            <div class="card">
              <div class="lbl">Dành cho ai</div>
              <p class="sub" style="margin:6px 0 0">Những người hoặc tổ chức có lượng người tiếp cận lớn: cộng đồng, bản tin newsletter, nhóm nhà phát triển hoặc agency triển khai giải pháp AI cho khách hàng.</p>
              <div class="lbl" style="margin-top:16px">Quyền lợi bạn nhận được</div>
              <p class="sub" style="margin:6px 0 0">Tỷ lệ chia sẻ doanh thu từ các khoản nạp tiền của người bạn giới thiệu, thanh toán trực tiếp bằng tiền mặt hàng tháng. Không giới hạn số lượng người giới thiệu.</p>
              <div class="lbl" style="margin-top:16px">Cách thức tham gia</div>
              <p class="sub" style="margin:6px 0 14px">Theo lời mời riêng. Hãy chia sẻ với chúng tôi về cộng đồng của bạn và cách bạn dự định giới thiệu mọi người đến với treg, chúng tôi sẽ liên hệ lại sớm nhất.</p>
              <a class="btn primary sm" href="https://forms.gle/5N3DyVPrNJkrGuxF6" target="_blank"
                 rel="noopener" @click="track('affiliate_apply_clicked')" style="text-decoration:none">Đăng ký làm đối tác liên kết</a>
            </div>
            <p class="sub" style="margin:12px 0 0">Bạn chỉ muốn giới thiệu cho bạn bè? Chương trình
              <a href="#" @click.prevent="refTab='friend'">giới thiệu bạn bè</a> tặng
              {{money(ref.terms.referrer_micro)}} tín dụng cho mỗi người bạn, không cần qua đơn đăng ký.</p>
          </div>

          <template v-if="refTab==='friend'">

          <p v-if="ref.loading" class="sub">Đang tải…</p>
          <div v-else style="max-width:720px">
            <div v-if="!ref.eligible" class="card" style="margin-top:14px">
              <div class="lbl">Tạo một đội ngũ để mở khóa liên kết giới thiệu</div>
              <p class="sub" style="margin:6px 0 12px">Phần thưởng giới thiệu được trả dưới dạng tín dụng vào đội ngũ mà bạn sở hữu, vì vậy bạn cần có một đội ngũ trước tiên.</p>
              <button class="btn primary sm" @click="go('orgs')">Đi đến quản lý đội ngũ</button>
            </div>

            <template v-else>
              <div class="card" style="margin-top:14px">
                <div class="lbl">Liên kết giới thiệu của bạn</div>
                <div style="display:flex;gap:8px;margin-top:8px">
                  <input readonly :value="ref.link" @focus="$event.target.select()"
                         style="flex:1;min-width:0;font-family:var(--mono);font-size:12px">
                  <button class="btn sm" @click="copyRefLink" style="flex:none">{{refCopied?'Đã chép':'Sao chép'}}</button>
                </div>
                <p class="sub" style="margin:10px 0 0" v-if="ref.credit_org">
                  Phần thưởng của bạn sẽ được cộng vào đội ngũ <b>{{ref.credit_org.name}}</b>.</p>
              </div>

              <div class="statgrid" style="margin-top:14px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
                <div class="stat"><div class="n">{{ref.totals.signed_up}}</div><div class="l">đã đăng ký</div></div>
                <div class="stat"><div class="n">{{ref.totals.topped_up}}</div><div class="l">đã nạp tiền</div></div>
                <div class="stat"><div class="n">{{money(ref.totals.earned_micro)}}</div><div class="l">đã nhận thưởng</div></div>
              </div>
              <p v-if="ref.totals.pending_micro" class="sub" style="margin:-8px 0 0">
                {{money(ref.totals.pending_micro)}} đang xử lý — phần thưởng sẽ mở khóa sau
                {{ref.terms.hold_days}} ngày kể từ khi bạn bè của bạn nạp tiền.</p>

              <div v-if="ref.cap.limit != null && ref.cap.paid >= ref.cap.limit" class="card"
                   style="margin-top:14px;border-color:var(--accent)">
                <div class="lbl">Bạn đã đạt giới hạn {{ref.cap.limit}} lượt giới thiệu</div>
                <p class="sub" style="margin:6px 0 0">Đó là mức tối đa của chương trình tự phục vụ thông thường. Nếu bạn có lượng người dùng lớn, hãy chuyển sang tab Đối tác liên kết ở trên — chúng tôi chi trả hoa hồng bằng tiền mặt.</p>
              </div>

              <div class="grp" style="margin:20px 0 8px">Danh sách bạn bè đã giới thiệu</div>
              <p v-if="!ref.referrals.length" class="sub" style="margin:0">
                Chưa có ai. Hãy chia sẻ liên kết của bạn ở trên.</p>
              <table v-else>
                <tr><th>Người dùng</th><th>Ngày đăng ký</th><th>Trạng thái</th><th style="text-align:right">Tiền thưởng</th></tr>
                <tr v-for="(r,i) in ref.referrals" :key="i">
                  <td>{{r.email || '—'}}</td>
                  <td class="sub" style="white-space:nowrap">{{bhistDate(r.signed_up_at)}}</td>
                  <td>{{refStatus(r)}}</td>
                  <td style="text-align:right;font-family:var(--mono);white-space:nowrap">
                    <span v-if="r.reward_micro">{{money(r.reward_micro)}}</span>
                    <span v-else class="muted">—</span>
                  </td>
                </tr>
              </table>
            </template>
          </div>
          </template>

</template>
