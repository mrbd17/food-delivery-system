// views/personal/sections/main.js

import openAvatarOverlay from "./avatar-overlay.js";
import * as service from "../../accounts/accountService.js";

export default function renderMain(container, state){

    const user = state.personal?.data?.data;

    if(!user){
        container.innerHTML = `
            <div class="skeleton-wrapper">
                <div class="skeleton-avatar"></div>
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="personal-wrapper">

            <h1 class="page-title">Personal info</h1>

            <!-- AVATAR -->
            <div class="avatar-section">
                <div class="avatar-container">

                    <img class="avatar-img"
                         src="${user.avatar || '/static/images/picture.jpg'}"/>

                    <div class="avatar-edit">
                        <svg viewBox="0 0 24 24" class="edit-icon">
                            <path d="M3 17.25V21h3.75L19.81 7.94
                                     16.06 4.19 3 17.25z"/>
                            <path d="M14.06 4.19l3.75 3.75"/>
                        </svg>
                    </div>

                </div>
            </div>

            <!-- LIST -->
            <div class="info-list">

                <div class="info-row" data-nav="name">
                    <div>
                        <p class="label">Name</p>
                        <p class="value">${user.first_name} ${user.last_name}</p>
                    </div>
                    <span class="arrow"></span>
                </div>

                <div class="info-row" data-nav="phone">
                    <div>
                        <p class="label">Phone number</p>
                        <p class="value">${user.phone}</p>
                    </div>
                    <span class="arrow"></span>
                </div>

                <div class="info-row" data-nav="email">
                    <div>
                        <p class="label">Email</p>
                        <p class="value">${user.email}</p>
                    </div>
                    <span class="arrow"></span>
                </div>

            </div>

        </div>
    `;

    const openOverlay = () => {
        openAvatarOverlay(async (file)=>{
            await service.changeAvatar(file);
            await service.loadPersonal();
        });
    };

    container.querySelector(".avatar-container")
        .addEventListener("click", openOverlay);

    container.querySelectorAll(".info-row")
        .forEach(row=>{
            row.addEventListener("click", ()=>{
                const nav = row.dataset.nav;
                history.pushState({}, "", `#/personal/${nav}`);
                window.dispatchEvent(new PopStateEvent("popstate"));
            });
        });
}